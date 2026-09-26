import os
from PIL import ImageGrab

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tray_shot.png")
ImageGrab.grab(all_screens=True).save(out)
