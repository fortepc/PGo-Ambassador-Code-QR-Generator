import tkinter as tk
from tkinter import filedialog, messagebox, Scale
from tkinter.ttk import Progressbar
from PIL import Image, ImageDraw, ImageFont
import qrcode

class QRCodeGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Ambassador Code QR Code Generator")
        self.base_image_path = ""
        self.codes_input = ""
        self.output_folder = ""
        self.font_size = 40  # Default font size

        self.create_widgets()

    def create_widgets(self):
        self.instructions_label = tk.Label(
            self.master,
            text="Welcome to the Ambassador Code QR Code Generator!\n\n"
            "Instructions:\n"
            "1. Click 'Pick File' to select a business card-sized base image (1050 x 600 pixels).\n"
            "2. Enter a list of unique codes (alphanumeric, comma or newline separated).\n"
            "3. Choose an output folder for the generated images.\n"
            "4. Adjust the font size using the slider.\n"
            "5. Click 'Run' to generate QR codes and images.",
            justify="left",
            padx=20,
            pady=20,
        )
        self.instructions_label.grid(row=0, column=0, columnspan=3)

        self.pick_file_button = tk.Button(self.master, text="Pick File", command=self.select_base_image)
        self.pick_file_button.grid(row=1, column=0, pady=10)

        self.selected_file_label = tk.Label(self.master, text="")
        self.selected_file_label.grid(row=1, column=1, columnspan=2, sticky="w", pady=10)

        self.code_label = tk.Label(self.master, text="Enter a list of unique codes:", padx=20, pady=10)
        self.code_label.grid(row=2, column=0, columnspan=3)

        self.code_entry = tk.Text(self.master, height=10, width=50)
        self.code_entry.grid(row=3, column=0, columnspan=3, pady=10)

        self.font_size_label = tk.Label(self.master, text="Adjust Font Size:")
        self.font_size_label.grid(row=4, column=0, pady=10)

        self.font_size_slider = Scale(self.master, from_=10, to=50, orient="horizontal", length=200, command=self.update_font_size)
        self.font_size_slider.set(self.font_size)
        self.font_size_slider.grid(row=4, column=1, columnspan=2, pady=10)

        self.output_folder_button = tk.Button(self.master, text="Select Output Folder", command=self.select_output_folder)
        self.output_folder_button.grid(row=5, column=0, pady=10)

        self.selected_output_folder_label = tk.Label(self.master, text="")
        self.selected_output_folder_label.grid(row=5, column=1, columnspan=2, sticky="w", pady=10)

        self.run_button = tk.Button(self.master, text="Run", command=self.generate_images)
        self.run_button.grid(row=6, column=2, pady=10)

        self.progress_bar = Progressbar(self.master, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=7, column=0, columnspan=3, pady=10)

    def select_base_image(self):
        self.base_image_path = filedialog.askopenfilename(
            title="Select Business Card Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )

        if self.base_image_path:
            self.selected_file_label.config(text=f"Selected File: {self.base_image_path}")

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")
        if self.output_folder:
            self.selected_output_folder_label.config(text=f"Selected Output Folder: {self.output_folder}")

    def update_font_size(self, value):
        self.font_size = int(value)

    def generate_images(self):
        self.codes_input = self.code_entry.get("1.0", "end-1c").strip()
        if not self.codes_input:
            self.show_error("Please enter at least one code.")
            return

        codes = [code.strip() for code in self.codes_input.replace(",", "\n").split("\n") if code.strip()]

        if not self.base_image_path:
            self.show_error("Base image not selected.")
            return

        if not self.output_folder:
            self.show_error("Output folder not selected.")
            return

        # Ensure the input image is of the correct size
        base_image = Image.open(self.base_image_path)
        target_width, target_height = 1050, 600
        if base_image.size != (target_width, target_height):
            # Resize if aspect ratio is correct
            if base_image.width / base_image.height == target_width / target_height:
                base_image = self.resize_image(base_image, target_width, target_height)
            else:
                self.show_error("Base image must be 1050 x 600 pixels.")
                return

        total_images = len(codes)
        self.progress_bar["maximum"] = total_images

        for i, code in enumerate(codes, start=1):
            qr_code = self.generate_qr_code(code)

            # Create a new RGBA image
            final_image = Image.open(self.base_image_path).convert("RGBA")

            # Apply QR code onto the image with transparent background
            qr_position = ((1050 - qr_code.size[0]) // 2, (600 - qr_code.size[1]) // 2)
            qr_background = Image.new("RGBA", final_image.size, (255, 255, 255, 0))
            qr_background.paste(qr_code, qr_position)
            final_image = Image.alpha_composite(final_image, qr_background)

            # Directly draw the code text on the final image
            draw = ImageDraw.Draw(final_image)
            font_size = self.font_size
            font = ImageFont.truetype("arial.ttf", size=int(font_size))

            # Calculate text position for center alignment at (524, 530)
            text_width, text_height = draw.textbbox((0, 0), code, font=font)[2:4]
            text_position = (
                524 - text_width // 2,
                530 - text_height // 2,
            )

            # Draw the code text in black at the target position
            draw.text(text_position, code, font=font, fill="black")

            # Save the final image
            output_path = f"{self.output_folder}/{code}.png"
            final_image.save(output_path)
            print(f"Image saved: {output_path}")

            self.progress_bar["value"] = i
            self.progress_bar.update()

        self.show_success_message()

    def generate_qr_code(self, code):
        url = f"https://store.pokemongolive.com/offer-redemption?passcode={code}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="transparent")

        return qr_img

    def resize_image(self, image, target_width, target_height):
        return image.resize((target_width, target_height), Image.ANTIALIAS)

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_success_message(self):
        messagebox.showinfo("Success", "Images generated successfully.")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()
