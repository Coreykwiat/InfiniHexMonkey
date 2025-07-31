import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import threading
import random
import csv
import os

def load_hex_pool(csv_filename="hex_bytes.csv"):
    if not os.path.exists(csv_filename):
        messagebox.showerror("Missing File", f"CSV file '{csv_filename}' not found.")
        return []

    try:
        with open(csv_filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                return [val.strip().upper() for val in row if val.strip()]
    except Exception as e:
        messagebox.showerror("CSV Error", f"Error reading hex values from CSV:\n{e}")
        return []

def is_valid_hex(s):
    try:
        bytes.fromhex(s)
        return True
    except ValueError:
        return False

class AnimatedGIF(tk.Label):
    def __init__(self, master, path, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.path = path
        self._load_gif()
        self._is_running = False
        self._frame_index = 0

    def _load_gif(self):
        self.image = Image.open(self.path)
        self.frames = []
        self.delays = []
        for frame in ImageSequence.Iterator(self.image):
            frame = frame.convert("RGBA")
            self.frames.append(ImageTk.PhotoImage(frame))
            delay = frame.info.get('duration', 100)  # ms delay per frame
            self.delays.append(delay)

    def start_animation(self):
        self._is_running = True
        self._animate()

    def stop_animation(self):
        self._is_running = False

    def _animate(self):
        if not self._is_running:
            return
        self.config(image=self.frames[self._frame_index])
        delay = self.delays[self._frame_index]
        self._frame_index = (self._frame_index + 1) % len(self.frames)
        self.after(delay, self._animate)

def background_task():
    try:
        start_hex = start_entry.get().strip()
        end_hex = end_entry.get().strip()
        file_ext = ext_entry.get().strip()
        size_limit_str = size_entry.get().strip()

        if not start_hex or not end_hex or not file_ext or not size_limit_str:
            messagebox.showerror("Input Error", "All fields must be filled out.")
            return

        if not is_valid_hex(start_hex):
            messagebox.showerror("Input Error", "Start header must be a valid hex string.")
            return

        if not is_valid_hex(end_hex):
            messagebox.showerror("Input Error", "End header must be a valid hex string.")
            return

        if not size_limit_str.isdigit():
            messagebox.showerror("Input Error", "Target file size must be a number.")
            return

        if not hex_pool:
            messagebox.showerror("Hex Pool Error", "Hex byte pool is empty. Check your CSV file.")
            return

        if not file_ext.startswith('.'):
            file_ext = '.' + file_ext

        size_limit = int(size_limit_str)
        start_bytes = bytes.fromhex(start_hex)
        end_bytes = bytes.fromhex(end_hex)

        filename = f"output{file_ext}"

        hex_byte_count = 0  # Initialize before loop

        with open(filename, 'ab') as f:
            while os.path.getsize(filename) < size_limit:
                hex_byte_count = random.randint(4, 16)
                selected_hex_values = random.choices(hex_pool, k=hex_byte_count)
                hex_bytes = bytes.fromhex(''.join(selected_hex_values))

                rand_number = random.randint(1000, 99999)
                rand_bytes = rand_number.to_bytes(4, byteorder='big')

                final_bytes = start_bytes + hex_bytes + rand_bytes + end_bytes
                f.write(final_bytes)

        final_size = os.path.getsize(filename)

        def update_ui():
            output_label.config(
                text=(
                    f"✅ File '{filename}' now has {final_size} bytes.\n"
                    f"🎯 Target size was {size_limit} bytes.\n"
                    f"🧱 Last Random Block: {hex_byte_count} bytes + 4-byte int\n"
                    f"Start ➡️ : {start_bytes.hex().upper()} | End ➡️: {end_bytes.hex().upper()}"
                )
            )
            gif_anim.stop_animation()
            gif_anim.pack_forget()

        root.after(0, update_ui)

    except Exception as e:
        def show_error():
            messagebox.showerror("Error", str(e))
            gif_anim.stop_animation()
            gif_anim.pack_forget()
        root.after(0, show_error)

def start_generation():
    gif_anim.pack(pady=10)
    gif_anim.start_animation()
    threading.Thread(target=background_task, daemon=True).start()

root = tk.Tk()
icon_img = tk.PhotoImage(file="monkey.png")
root.iconphoto(False, icon_img)
root.title("InfiniHexMonkey: Pillow GIF Animation")

tk.Label(root, text="Start Header (hex):").pack(pady=5)
start_entry = tk.Entry(root, width=40)
start_entry.pack()

tk.Label(root, text="End Header (hex):").pack(pady=5)
end_entry = tk.Entry(root, width=40)
end_entry.pack()

tk.Label(root, text="File Extension (e.g., .bin):").pack(pady=5)
ext_entry = tk.Entry(root, width=20)
ext_entry.pack()

tk.Label(root, text="Target File Size (bytes):").pack(pady=5)
size_entry = tk.Entry(root, width=20)
size_entry.pack()

tk.Button(root, text="Make the Monkey Work", command=start_generation).pack(pady=10)

output_label = tk.Label(root, text="", wraplength=600, justify="left", fg="darkgreen")
output_label.pack(padx=10, pady=10)

hex_pool = load_hex_pool("hex_bytes.csv")

gif_anim = AnimatedGIF(root, "monkey.gif")

root.mainloop()
