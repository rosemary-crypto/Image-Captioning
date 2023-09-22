import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import json

class ImageCaptioningTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Captioning Annotation Tool")

        self.image_folder = ""
        self.images = []
        self.current_image_index = 0
        self.captions_per_image = 3

        self.load_images_button = tk.Button(root, text="Load Images", command=self.load_images)
        self.load_images_button.pack(pady=10)

        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()

        self.caption_entry = tk.Entry(root, width=40)
        self.caption_entry.pack(pady=10)
        self.caption_entry.bind("<Button-1>", self.on_caption_entry_click) 

        self.save_button = tk.Button(root, text="Save Caption", command=self.save_caption)
        self.save_button.pack()

        self.next_button = tk.Button(root, text="Next Image", command=self.next_image)
        self.next_button.pack(pady=10)

        self.load_images()

    def on_caption_entry_click(self, event):
        if self.caption_entry.get() == "Enter caption here":
            self.caption_entry.delete(0, tk.END)
            self.caption_entry.config(fg="black")  # Change text color to black
        self.caption_entry.focus_set() 
        
    def load_images(self):
        self.image_folder = filedialog.askdirectory(title="Select Image Folder")
        if self.image_folder:
            self.images = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            self.images = [image for image in self.images if self.check_caption_count(image) < 3]  # Filter images with less than 3 captions
            if self.images:
                self.current_image_index = 0  # Reset the index to the first image
                self.show_image()
                self.caption_entry.focus_set()

    def check_caption_count(self, image_name):
        annotations = {}
        if os.path.exists("annotations.json"):
            with open("annotations.json", "r") as f:
                annotations = json.load(f)
        return len(annotations.get(image_name, []))
    
    def show_image(self):
        image_path = os.path.join(self.image_folder, self.images[self.current_image_index])
        img = Image.open(image_path)
        img = img.resize((400, 400), Image.LANCZOS)  # Use LANCZOS resampling filter
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.caption_entry.config(state=tk.NORMAL)
        self.update_caption_entry()
        self.caption_entry.focus_set()

    def update_caption_entry(self):
        if self.get_caption_count() >= self.captions_per_image:
            self.caption_entry.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
        else:
            self.caption_entry.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

    def get_caption_count(self):
        image_name = self.images[self.current_image_index]
        annotations = self.load_annotations()
        return len(annotations.get(image_name, []))

    def save_caption(self):
        caption = self.caption_entry.get()
        if caption.strip() == "":
            messagebox.showwarning("Warning", "Please enter a caption.")
            return

        image_name = self.images[self.current_image_index]
        annotations = self.load_annotations()
        if len(annotations.get(image_name, [])) < self.captions_per_image:
            annotations[image_name] = annotations.get(image_name, [])
            annotations[image_name].append(caption)

            with open("annotations.json", "w") as f:
                json.dump(annotations, f, indent=4)

            self.caption_entry.delete(0, tk.END)
            self.update_caption_entry()
            if self.get_caption_count() >= self.captions_per_image:
                self.next_image()

    def load_annotations(self):
        annotations = {}
        if os.path.exists("annotations.json"):
            with open("annotations.json", "r") as f:
                annotations = json.load(f)
        return annotations

    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCaptioningTool(root)
    root.mainloop()
