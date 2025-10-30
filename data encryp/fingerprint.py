import cv2
import numpy as np
from tkinter import Tk, filedialog

def load_image_grayscale(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Can't open: {path}")
    return img

def resize_to_same(a, b):
    # Resize b to a's size
    h, w = a.shape[:2]
    return cv2.resize(b, (w, h), interpolation=cv2.INTER_AREA)

# 1) Alpha blend
def alpha_blend(img1, img2, alpha=0.5):
    img2 = resize_to_same(img1, img2)
    blended = cv2.addWeighted(img1, alpha, img2, 1-alpha, 0)
    return blended

# 2) Checkerboard / tile interleave
def checkerboard_merge(img1, img2, tile_size=20):
    img2 = resize_to_same(img1, img2)
    h, w = img1.shape[:2]
    out = np.zeros_like(img1)
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            y2 = min(y + tile_size, h)
            x2 = min(x + tile_size, w)
            # choose tile from img1 or img2 depending on checkerboard parity
            if ((x // tile_size) + (y // tile_size)) % 2 == 0:
                out[y:y2, x:x2] = img1[y:y2, x:x2]
            else:
                out[y:y2, x:x2] = img2[y:y2, x:x2]
    return out

# 3) Random patch mosaic
def random_patch_merge(img1, img2, patch_size=40, patch_frac=0.35, seed=None):
    """
    patch_frac: fraction of patches to replace by img2
    """
    if seed is not None:
        np.random.seed(seed)
    img2 = resize_to_same(img1, img2)
    h, w = img1.shape[:2]
    out = img1.copy()
    # compute grid
    ys = list(range(0, h, patch_size))
    xs = list(range(0, w, patch_size))
    patches = [(y, x) for y in ys for x in xs]
    num_replace = int(len(patches) * patch_frac)
    replace_idx = np.random.choice(len(patches), size=num_replace, replace=False)
    for idx in replace_idx:
        y, x = patches[idx]
        y2 = min(y + patch_size, h)
        x2 = min(x + patch_size, w)
        out[y:y2, x:x2] = img2[y:y2, x:x2]
    return out

def pick_files():
    Tk().withdraw()
    p1 = filedialog.askopenfilename(title="Select first image (source 1)")
    p2 = filedialog.askopenfilename(title="Select second image (source 2)")
    return p1, p2

def main():
    print("Select two images to merge (grayscale).")
    p1, p2 = pick_files()
    if not p1 or not p2:
        print("No files selected. Exiting.")
        return

    img1 = load_image_grayscale(p1)
    img2 = load_image_grayscale(p2)

    # Parameters - change these to make merging stronger/weaker
    alpha = 0.45           # for alpha blend (0..1)
    tile_size = 16         # for checkerboard
    patch_size = 24        # for random patches
    patch_frac = 0.45      # fraction of patches taken from img2

    # produce three variants
    blended = alpha_blend(img1, img2, alpha=alpha)
    checker = checkerboard_merge(img1, img2, tile_size=tile_size)
    random_mosaic = random_patch_merge(img1, img2, patch_size=patch_size, patch_frac=patch_frac, seed=42)

    # Show previews (press any key to cycle)
    cv2.imshow("Alpha Blend (press any key)", blended)
    cv2.waitKey(0)

    cv2.imshow("Checkerboard Merge (press any key)", checker)
    cv2.waitKey(0)

    cv2.imshow("Random Patch Mosaic (press any key)", random_mosaic)
    cv2.waitKey(0)

    cv2.destroyAllWindows()

    # Save chosen output
    print("Choose output to save: (1)alpha (2)checker (3)random (0)none")
    choice = input("Enter 1/2/3/0: ").strip()
    out_map = {'1': blended, '2': checker, '3': random_mosaic}
    if choice in out_map:
        out_img = out_map[choice]
        save_path = filedialog.asksaveasfilename(title="Save merged image as", defaultextension=".png",
                                                 filetypes=[("PNG files","*.png"),("JPEG","*.jpg;*.jpeg")])
        if save_path:
            cv2.imwrite(save_path, out_img)
            print(f"Saved merged image to: {save_path}")
        else:
            print("Save cancelled.")
    else:
        print("No output saved. Exiting.")


