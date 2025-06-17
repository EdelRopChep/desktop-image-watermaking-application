import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from io import BytesIO
import sys


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermark Tool")
        self.root.geometry("900x650")

        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Variables
        self.image_path = None
        self.watermarked_image = None
        self.display_image = None
        self.watermark_color = (255, 255, 255)  # Default white text
        self.bg_color = None  # Default no background
        self.bg_opacity = 0  # Default transparent background

        # Create UI
        self.create_widgets()

    def on_close(self):
        """Clean up when window is closed"""
        self.root.destroy()
        sys.exit(0)

    def create_widgets(self):
        # Image display frame
        self.image_frame = tk.Frame(self.root, bg='gray')
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Controls frame
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Row 1 controls
        row1 = tk.Frame(self.controls_frame)
        row1.pack(fill=tk.X, pady=5)

        # Upload button
        self.upload_btn = tk.Button(row1, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        # Watermark text
        tk.Label(row1, text="Watermark Text:").pack(side=tk.LEFT, padx=5)
        self.watermark_entry = tk.Entry(row1, width=20)
        self.watermark_entry.pack(side=tk.LEFT, padx=5)

        # Font size
        tk.Label(row1, text="Size:").pack(side=tk.LEFT, padx=5)
        self.font_size = tk.Spinbox(row1, from_=10, to=100, width=5)
        self.font_size.pack(side=tk.LEFT, padx=5)
        self.font_size.delete(0, tk.END)
        self.font_size.insert(0, "30")

        # Text color button
        self.color_btn = tk.Button(row1, text="Text Color", command=self.choose_text_color)
        self.color_btn.pack(side=tk.LEFT, padx=5)

        # Row 2 controls
        row2 = tk.Frame(self.controls_frame)
        row2.pack(fill=tk.X, pady=5)

        # Background color button
        self.bg_color_btn = tk.Button(row2, text="BG Color", command=self.choose_bg_color)
        self.bg_color_btn.pack(side=tk.LEFT, padx=5)

        # BG Opacity
        tk.Label(row2, text="BG Opacity:").pack(side=tk.LEFT, padx=5)
        self.bg_opacity_slider = tk.Scale(row2, from_=0, to=100, orient=tk.HORIZONTAL)
        self.bg_opacity_slider.pack(side=tk.LEFT, padx=5)
        self.bg_opacity_slider.set(0)

        # Text Opacity
        tk.Label(row2, text="Text Opacity:").pack(side=tk.LEFT, padx=5)
        self.text_opacity_slider = tk.Scale(row2, from_=10, to=100, orient=tk.HORIZONTAL)
        self.text_opacity_slider.pack(side=tk.LEFT, padx=5)
        self.text_opacity_slider.set(50)

        # Position
        tk.Label(row2, text="Position:").pack(side=tk.LEFT, padx=5)
        self.position_var = tk.StringVar()
        self.position_dropdown = ttk.Combobox(row2,
                                              textvariable=self.position_var,
                                              values=["Top Left", "Top Right",
                                                      "Bottom Left", "Bottom Right",
                                                      "Center"])
        self.position_dropdown.pack(side=tk.LEFT, padx=5)
        self.position_dropdown.current(4)  # Default to Center

        # Row 3 controls
        row3 = tk.Frame(self.controls_frame)
        row3.pack(fill=tk.X, pady=5)

        # Apply watermark button
        self.apply_btn = tk.Button(row3, text="Apply Watermark", command=self.apply_watermark)
        self.apply_btn.pack(side=tk.LEFT, padx=5)

        # Save button
        self.save_btn = tk.Button(row3, text="Save Image", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.image_path = file_path
            self.show_image()

    def show_image(self, image=None):
        if image is None:
            if not self.image_path:
                return
            image = Image.open(self.image_path)

        # Resize to fit the display area
        max_width = self.image_frame.winfo_width() - 20
        max_height = self.image_frame.winfo_height() - 20

        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        self.display_image = ImageTk.PhotoImage(resized_image)
        self.image_label.config(image=self.display_image)

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[0]:
            self.watermark_color = tuple(int(c) for c in color[0])

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[0]:
            self.bg_color = tuple(int(c) for c in color[0])
        else:
            self.bg_color = None

    def apply_watermark(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please upload an image first")
            return

        watermark_text = self.watermark_entry.get()
        if not watermark_text:
            messagebox.showerror("Error", "Please enter watermark text")
            return

        try:
            # Open the image
            image = Image.open(self.image_path).convert("RGBA")

            # Create a transparent layer for watermark
            watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)

            # Get font (try Arial, fallback to default)
            try:
                font = ImageFont.truetype("arial.ttf", int(self.font_size.get()))
            except:
                font = ImageFont.load_default()

            # Calculate text size using textbbox
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            position = self.position_var.get()
            margin = 20
            padding = 10  # Space between text and background border

            if position == "Top Left":
                x = margin
                y = margin
            elif position == "Top Right":
                x = image.width - text_width - margin
                y = margin
            elif position == "Bottom Left":
                x = margin
                y = image.height - text_height - margin
            elif position == "Bottom Right":
                x = image.width - text_width - margin
                y = image.height - text_height - margin
            else:  # Center
                x = (image.width - text_width) // 2
                y = (image.height - text_height) // 2

            # Add background if color is selected
            if self.bg_color and self.bg_opacity_slider.get() > 0:
                bg_opacity = int(255 * (self.bg_opacity_slider.get() / 100))
                bg_fill = (*self.bg_color, bg_opacity)

                # Draw rectangle slightly larger than text
                draw.rectangle(
                    [x - padding, y - padding,
                     x + text_width + padding, y + text_height + padding],
                    fill=bg_fill
                )

            # Add text with opacity
            text_opacity = int(255 * (self.text_opacity_slider.get() / 100))
            draw.text((x, y), watermark_text, font=font,
                      fill=(*self.watermark_color, text_opacity))

            # Combine images
            self.watermarked_image = Image.alpha_composite(image, watermark)

            # Display the result
            self.show_image(self.watermarked_image)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def save_image(self):
        if not hasattr(self, 'watermarked_image') or not self.watermarked_image:
            messagebox.showerror("Error", "No watermarked image to save")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    self.watermarked_image.convert("RGB").save(file_path)
                else:
                    self.watermarked_image.save(file_path)
                messagebox.showinfo("Success", "Image saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WatermarkApp(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)