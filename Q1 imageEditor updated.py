
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps

class ImageFilterBase:
    def apply(self, image):
        raise NotImplementedError("Subclasses must implement this method.")

class GrayscaleFilter(ImageFilterBase):
    def apply(self, image):
        return image.convert("L")

class InvertFilter(ImageFilterBase):
    def apply(self, image):
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
            inverted = ImageOps.invert(rgb)
            r2, g2, b2 = inverted.split()
            return Image.merge("RGBA", (r2, g2, b2, a))
        elif image.mode == 'RGB':
            return ImageOps.invert(image)
        else:
            return ImageOps.invert(image.convert("RGB"))

class BlurFilter(ImageFilterBase):
    def apply(self, image):
        return image.filter(ImageFilter.BLUR)

class ContourFilter(ImageFilterBase):
    def apply(self, image):
        return image.filter(ImageFilter.CONTOUR)

# This is the main application window using tkinter
class AkramImageEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Akram's Image Editor")
        self.geometry("800x600")

        self.image = None
        self.tk_image = None
        self.zoom_level = 1.0
        self.zooming_in = True
        self.history = []
        self.future = []
        self.start_x = None
        self.start_y = None
        self.crop_rect = None

        self.setup_gui()

    def setup_gui(self):
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Open Image", command=self.open_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Crop", command=self.activate_crop_mode).pack(side=tk.LEFT, padx=5)

        self.zoom_button = tk.Button(button_frame, text="Zoom In", command=self.toggle_zoom)
        self.zoom_button.pack(side=tk.LEFT, padx=5)

        filters = [
            ("Grayscale", GrayscaleFilter()),
            ("Invert Colors", InvertFilter()),
            ("Blur", BlurFilter()),
            ("Contour", ContourFilter())
        ]
        for name, filter_obj in filters:
            tk.Button(button_frame, text=name, command=lambda f=filter_obj: self.apply_filter(f)).pack(side=tk.LEFT, padx=5)

# This canvas is where we draw and show the loaded or edited image
        self.canvas = tk.Canvas(self, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            try:
                self.image = Image.open(file_path).convert("RGBA")
                self.zoom_level = 1.0
                self.history.clear()
                self.future.clear()
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image:\n{str(e)}")

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                try:
                    self.image.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save image:\n{str(e)}")
        else:
            messagebox.showwarning("No Image", "Please open an image first.")

    def display_image(self):
        if self.image:
            w, h = self.image.size
            resized = self.image.resize((int(w * self.zoom_level), int(h * self.zoom_level)))
            self.tk_image = ImageTk.PhotoImage(resized)
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, image=self.tk_image)

    def apply_filter(self, filter_obj: ImageFilterBase):
        if self.image:
            try:
                self.save_state()
                self.image = filter_obj.apply(self.image)
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"Filter failed:\n{str(e)}")
        else:
            messagebox.showwarning("No Image", "Open an image before applying filters.")

# Keep track of previous image state so user can undo
    def save_state(self):
        if self.image:
            self.history.append(self.image.copy())
            self.future.clear()

# Reverts the image to its last saved state
    def undo(self):
        if self.history:
            self.future.append(self.image.copy())
            self.image = self.history.pop()
            self.display_image()

# Restores the image to its next state if undo was pressed
    def redo(self):
        if self.future:
            self.history.append(self.image.copy())
            self.image = self.future.pop()
            self.display_image()

    def on_mouse_wheel(self, event):
        if self.image:
            if event.num == 4 or event.delta > 0:
                self.zoom_level *= 1.1
            elif event.num == 5 or event.delta < 0:
                self.zoom_level /= 1.1
            self.display_image()

# This method toggles zoom level when the Zoom button is clicked
    def toggle_zoom(self):
        if self.image:
            if self.zooming_in:
                self.zoom_level *= 1.2
                self.zoom_button.config(text="Zoom Out")
            else:
                self.zoom_level /= 1.2
                self.zoom_button.config(text="Zoom In")
            self.zooming_in = not self.zooming_in
            self.display_image()

# Enable cropping: user can draw a box on the image to crop
    def activate_crop_mode(self):
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
        self.canvas.bind("<ButtonRelease-1>", self.finish_crop)

    def start_crop(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = None

    def draw_crop_rect(self, event):
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='red')

    def finish_crop(self, event):
        if not self.image:
            return

        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        bbox = self.canvas.bbox(self.crop_rect)
        if bbox:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.image.size
            x_ratio = img_width / canvas_width
            y_ratio = img_height / canvas_height

            left = int(x1 * x_ratio)
            upper = int(y1 * y_ratio)
            right = int(x2 * x_ratio)
            lower = int(y2 * y_ratio)

            self.save_state()
            self.image = self.image.crop((left, upper, right, lower))
            self.zoom_level = 1.0
            self.display_image()

if __name__ == "__main__":
    app = AkramImageEditor()
    app.mainloop()
