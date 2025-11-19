import numpy as np
from PIL import Image
import math
import sys

def compute_dfv(block):

    Flow_x = (block[0,2] + block[1,2] + block[2,2]) - (block[0,0] + block[1,0] + block[2,0])
    Flow_y = (block[2,0] + block[2,1] + block[2,2]) - (block[0,0] + block[0,1] + block[0,2])
    return int(Flow_x), int(Flow_y)

def encode_tpms(carrier_path, secret_path, out_path):

    carrier = Image.open(carrier_path).convert("YCbCr")
    secret  = Image.open(secret_path).convert("RGB")
    secret  = secret.resize(carrier.size)

    Y, Cb, Cr = carrier.split()

    Y = np.array(Y,  dtype=np.uint8)
    Cb = np.array(Cb, dtype=np.uint8)
    Cr = np.array(Cr, dtype=np.uint8)

    S = np.array(secret, dtype=np.uint8)

    h, w = Y.shape
    Y_mod = Y.copy()

    for y in range(0, h-2, 3):
        for x in range(0, w-2, 3):

            R, G, B = S[y, x]
            theta = (R / 255) * 2 * math.pi
            rho   = G / 255

            theta_q = int((theta / (2 * math.pi)) * 255)
            rho_q   = int(rho * 255)

            block = Y_mod[y:y+3, x:x+3].astype(float)

            for _ in range(6):
                Fx, Fy = compute_dfv(block)
                dx = theta_q - Fx
                dy = rho_q - Fy

                block[:, 2] += dx * 0.1
                block[:, 0] -= dx * 0.1

                block[2, :] += dy * 0.1
                block[0, :] -= dy * 0.1

                block = np.clip(block, 0, 255)

            Y_mod[y:y+3, x:x+3] = block.astype(np.uint8)

    # Merge modified Y with original Cb/Cr → RGB
    Y_img  = Image.fromarray(Y_mod, "L")
    Cb_img = Image.fromarray(Cb, "L")
    Cr_img = Image.fromarray(Cr, "L")

    stego = Image.merge("YCbCr", (Y_img, Cb_img, Cr_img)).convert("RGB")
    stego.save(out_path)

    print("[+] Color stego image saved:", out_path)




def decode_tpms(stego_path, out_path):

    stego = Image.open(stego_path).convert("YCbCr")
    Y, Cb, Cr = stego.split()

    Y = np.array(Y, dtype=np.uint8)

    h, w = Y.shape
    secret = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(0, h-2, 3):
        for x in range(0, w-2, 3):

            block = Y[y:y+3, x:x+3]
            Fx, Fy = compute_dfv(block)

            theta_q = max(0, min(255, Fx))
            rho_q   = max(0, min(255, Fy))

            R = theta_q
            G = rho_q
            B = 255 - G

            secret[y:y+3, x:x+3] = (R, G, B)

    Image.fromarray(secret).save(out_path)
    print("[+] Decoded secret saved:", out_path)



def main():
    print("TPMS Steganography (Improved Near-Lossless Version)")
    print("===================================================")
    print("Choose mode:")
    print("  1 = Encode")
    print("  2 = Decode")

    mode = input("Enter mode (1/2): ").strip()

    if mode == "1":
        carrier_path = input("Enter carrier image path: ").strip()
        secret_path  = input("Enter secret image path: ").strip()
        out_path     = input("Enter output stego image path: ").strip()
        encode_tpms(carrier_path, secret_path, out_path)

    elif mode == "2":
        stego_path = input("Enter stego image path: ").strip()
        out_path   = input("Enter recovered secret output path: ").strip()
        decode_tpms(stego_path, out_path)

    else:
        print("Invalid mode selected.")


if __name__ == "__main__":
    main()
