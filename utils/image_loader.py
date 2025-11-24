from PIL import Image, ImageTk

class ImageLoader:
    @staticmethod
    def load_image(path):
        try:
            img = Image.open(path)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None