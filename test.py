import numpy as np
from PIL import Image
import sys
import os

def resize_and_prepare(img_path, size=(1024, 1024)):
    img = Image.open(img_path).convert('RGB')
    img = img.resize(size, Image.LANCZOS)
    return np.array(img, dtype=np.int16)

def save_image(array, output_path):
    array = np.clip(array, 0, 255).astype(np.uint8)
    Image.fromarray(array).save(output_path)
    print(f"Saved result to: {output_path}")

def main():
    op = input("Enter operation (+ or -): ").strip()
    if op not in ['+', '-']:
        print("Invalid input. Please enter '+' or '-'.")
        sys.exit(1)

    img1_path = input("Enter path to first image: ").strip()
    img2_path = input("Enter path to second image: ").strip()

    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print("One or both image paths do not exist.")
        sys.exit(1)

    # Load and preprocess
    img1 = resize_and_prepare(img1_path)
    img2 = resize_and_prepare(img2_path)

    if op == '+':
        result = img1 + img2
        out_name = "added_image.png"
    else:
        result = img1 - img2
        out_name = "subtracted_image.png"

    # Save output
    save_image(result, out_name)

if __name__ == "__main__":
    main()
