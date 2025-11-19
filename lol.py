import numpy as np
from PIL import Image, ImageFilter
import math


#THIS WILL EFFECT THE MORE SIGNIFICANT BITS, LOWER TO EFFECT THE LEAST
MAX_DFV_RESISTANT = 20.0

def compute_dfv(block):
    Fx = float((block[0, 2] + block[1, 2] + block[2, 2]) - (block[0, 0] + block[1, 0] + block[2, 0]))
    Fy = float((block[2, 0] + block[2, 1] + block[2, 2]) - (block[0, 0] + block[0, 1] + block[0, 2]))
    return Fx, Fy


def rgb_to_theta_rho(R, G, B):
    theta = (float(R) / 255.0) * 2.0 * math.pi
    rho = float(G) / 255.0
    return theta, rho


def theta_rho_to_rgb(theta, rho):
    R = int(round((theta / (2.0 * math.pi)) * 255.0)) % 256
    G = int(round(max(0.0, min(1.0, rho)) * 255.0))
    B = int(max(0, min(255, 255 - G)))
    return R, G, B


def make_dfv_pattern(dx, dy):

    v, u = dx / 6.0, dy / 6.0
    patt = np.zeros((3, 3))
    patt[0, 2] += v;
    patt[1, 2] += v;
    patt[2, 2] += v;
    patt[0, 0] -= v;
    patt[1, 0] -= v;
    patt[2, 0] -= v

    patt[2, 0] += u;
    patt[2, 1] += u;
    patt[2, 2] += u;
    patt[0, 0] -= u;
    patt[0, 1] -= u;
    patt[0, 2] -= u
    return patt


def adjust_block(block_in, dx, dy, iters=6, step=0.9):
    block = block_in.astype(float).copy()
    for _ in range(iters):
        Fx, Fy = compute_dfv(block)
        error_dx = (dx - Fx) * step
        error_dy = (dy - Fy) * step
        patt = make_dfv_pattern(error_dx, error_dy)
        block = np.clip(block + patt, 0, 255)
    return block


def encode_robust(carrier_path, secret_path, out_path, MAX_DFV=MAX_DFV_RESISTANT, REDUNDANCY=3):
    carrier = Image.open(carrier_path).convert("RGB")
    secret = Image.open(secret_path).convert("RGB")

    w_c, h_c = carrier.size
    block_span = 3 * REDUNDANCY
    w_s = w_c // block_span
    h_s = h_c // block_span

    print(f"[i] Resizing secret to {w_s}x{h_s} (Redundancy level {REDUNDANCY})")
    secret = secret.resize((w_s, h_s), Image.LANCZOS)

    carrier_ycbcr = carrier.convert("YCbCr")
    Y, Cb, Cr = carrier_ycbcr.split()
    Y_arr = np.array(Y, dtype=np.float32)
    S_arr = np.array(secret, dtype=np.uint8)

    for sy in range(h_s):
        for sx in range(w_s):
            R, G, B = S_arr[sy, sx]
            theta, rho = rgb_to_theta_rho(R, G, B)
            dx = rho * math.cos(theta) * MAX_DFV
            dy = rho * math.sin(theta) * MAX_DFV
            cy_start = sy * block_span
            cx_start = sx * block_span

            for ry in range(REDUNDANCY):
                for rx in range(REDUNDANCY):
                    y = cy_start + (ry * 3)
                    x = cx_start + (rx * 3)

                    if y + 3 > h_c or x + 3 > w_c: continue

                    block = Y_arr[y:y + 3, x:x + 3]
                    Y_arr[y:y + 3, x:x + 3] = adjust_block(block, dx, dy, iters=6)

    stego = Image.merge("YCbCr", (Image.fromarray(np.clip(Y_arr, 0, 255).astype(np.uint8)), Cb, Cr)).convert("RGB")
    stego.save(out_path, quality=95)
    print(f"[+] Robust and LSB-resistant Stego saved to {out_path} (MAX_DFV={MAX_DFV})")


def decode_robust(stego_path, out_path, MAX_DFV=MAX_DFV_RESISTANT, REDUNDANCY=3):
    stego = Image.open(stego_path).convert("YCbCr")
    Y_arr = np.array(stego.split()[0], dtype=np.float32)
    h_c, w_c = Y_arr.shape

    block_span = 3 * REDUNDANCY
    h_s = h_c // block_span
    w_s = w_c // block_span

    secret_buffer = np.zeros((h_s, w_s, 3), dtype=np.uint8)

    print("[i] Decoding with voting system...")

    for sy in range(h_s):
        for sx in range(w_s):
            fx_votes = []
            fy_votes = []
            cy_start = sy * block_span
            cx_start = sx * block_span
            for ry in range(REDUNDANCY):
                for rx in range(REDUNDANCY):
                    y = cy_start + (ry * 3)
                    x = cx_start + (rx * 3)
                    if y + 3 > h_c or x + 3 > w_c: continue
                    Fx, Fy = compute_dfv(Y_arr[y:y + 3, x:x + 3])
                    fx_votes.append(Fx)
                    fy_votes.append(Fy)
            if not fx_votes: continue
            fx_final = np.median(fx_votes)
            fy_final = np.median(fy_votes)
            rho = math.sqrt(fx_final ** 2 + fy_final ** 2) / (MAX_DFV + 1e-12)
            theta = math.atan2(fy_final, fx_final)
            secret_buffer[sy, sx] = theta_rho_to_rgb(theta % (2 * math.pi), rho)

    img = Image.fromarray(secret_buffer)
    img = img.resize((w_c, h_c), Image.NEAREST)
    img.save(out_path)
    print(f"[+] Recovered secret saved to {out_path}")


if __name__ == "__main__":
    mode = input("1=Encode, 2=Decode: ")

    if mode == '1':
        cover_image = input("Where is your cover image located? ")
        secret = input("What is the Message to encode? ")
        output_name = input("What is the output name? ")
        encode_robust(cover_image, secret, output_name, REDUNDANCY=3)
    else:
        decode_image = input("Where is the image to decode? ")
        decoded_output = input("What is the decoded image name? ")
        decode_robust(decode_image, decoded_output, REDUNDANCY=3)