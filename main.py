import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from rembg import remove

class ImageBackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Background Remover")
        self.root.geometry("1200x600")  # Adjust the size of the window

        # Frames for the original and edited image previews
        self.original_image_frame = tk.Frame(self.root, width=600, height=600)
        self.original_image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.edited_image_frame = tk.Frame(self.root, width=600, height=600)
        self.edited_image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvases for images
        self.original_canvas = tk.Canvas(self.original_image_frame, cursor="arrow")
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        self.edited_canvas = tk.Canvas(self.edited_image_frame, cursor="cross")
        self.edited_canvas.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.upload_button = tk.Button(self.root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(side=tk.BOTTOM, pady=10)
        self.download_button = tk.Button(self.root, text="Download Edited Image", command=self.download_image, state=tk.DISABLED)
        self.download_button.pack(side=tk.BOTTOM, pady=10)

        # Initialize image-related variables
        self.input_image = None
        self.processed_image = None
        self.cropped_image = None

        # Initialize cropping-related variables
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.rect_id = None
        self.moving = False

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.input_image = Image.open(file_path)
            self.processed_image = remove(self.input_image)
            self.display_image(self.input_image, self.original_canvas)
            self.display_image(self.processed_image, self.edited_canvas)

            # Reset cropping state
            self.cropped_image = None
            self.download_button.config(state=tk.DISABLED)

            # Bind mouse events for cropping on the edited canvas
            self.edited_canvas.bind("<ButtonPress-1>", self.start_crop)
            self.edited_canvas.bind("<B1-Motion>", self.move_crop)
            self.edited_canvas.bind("<ButtonRelease-1>", self.end_crop)

    def display_image(self, image, canvas):
        canvas.delete("all")  # Clear the canvas
        tk_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=tk_image, anchor=tk.NW)
        canvas.image = tk_image  # Keep a reference
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

    def start_crop(self, event):
        self.start_x = self.edited_canvas.canvasx(event.x)
        self.start_y = self.edited_canvas.canvasy(event.y)
        if not self.rect:
            self.rect = self.edited_canvas.create_rectangle(self.start_x, self.start_y, self.start_x+1, self.start_y+1, outline='red')
        else:
            self.moving = True

    def move_crop(self, event):
        curX = self.edited_canvas.canvasx(event.x)
        curY = self.edited_canvas.canvasy(event.y)
        if self.moving:
            # When moving the rectangle, reset it
            self.edited_canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)
        else:
            # Create rectangle if not already created
            self.edited_canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def end_crop(self, event):
        self.moving = False
        # Finalize the coordinates of the crop rectangle and crop
        x1, y1, x2, y2 = self.edited_canvas.coords(self.rect)
        self.crop_image(x1, y1, x2, y2)

    def crop_image(self, x1, y1, x2, y2):
        # The PIL crop method takes the left, upper, right, and lower pixel coordinates
        self.cropped_image = self.processed_image.crop((x1, y1, x2, y2))
        self.display_image(self.cropped_image, self.edited_canvas)
        self.download_button.config(state=tk.NORMAL)

    def download_image(self):
        if self.cropped_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                self.cropped_image.save(save_path)

root = tk.Tk()
app = ImageBackgroundRemoverApp(root)
root.mainloop()
