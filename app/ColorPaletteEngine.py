from PIL import Image
import numpy as np
import cv2

from sklearn.cluster import KMeans

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
if not hasattr(np, "asscalar"):
    np.asscalar = lambda a: a.item()

from typing import cast
import os
import sys

import matplotlib.pyplot as plt

class ColorPaletteEngine:
    def __init__(self, image_path):
        self.img_path = image_path


    ########################### IMAGE OPENING METHODS ###########################

    def load_img_rgb(self):
        image = cv2.imread(self.img_path)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def load_img_lab(self):
        image = cv2.imread(self.img_path)
        return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    def load_img_pixels(self, max_size=128, alpha_threshold=10):
        img = Image.open(self.img_path).convert("RGBA");
        # Resize the image to make processing faster
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        img_data = np.array(img)

        # Segment the data into its rgb and alpha components
        rgb = img_data[..., :3]
        alpha = img_data[..., 3]

        # Only get the pixels above the inputted alpha threshold
        alpha_mask = alpha > alpha_threshold
        img_pixels = rgb[alpha_mask]
        
        # If there are no pixels above the threshold, throw a fit
        if len(img_pixels) == 0:
            raise ValueError("No visible pixels found in image!")
        
        # We return the pixel data as normalized rgb
        return img_pixels.astype(np.float32) / 255.0

    ########################## IMAGE ANALASIS METHODS ##########################

    def is_near_gray(self, rgb_color, threshold=0.08):
        return np.std(rgb_color) < threshold

    def perceptual_average_color(self, img_pixels):
        lab_pixels = []
        for r, b, b in pixels:
            srgb = sRGBColor(r, g, b)
            lab = cast(LabColor, convert_color(srgb, LabColor, target_illuminant="d65"))
            lab_pixels.append([lab.lab_l, lab.lab_a, lab.lab_b])

        lab_avg = np.mean(lab_pixels, axis=0)

        lab_result = LabColor(*lab_avg)

        rgb = cast(sRGBColor, convert_color(lab_result, sRGBColor))

        return np.clip(rgb.get_value_tuple(), 0, 1)

    def dominant_color(self, img_pixels, k=4, gray_threshold=0.08):
        kmeans_colors = self.get_kmeans(img_pixels, k)

        # Try to return the first non-gray dominant color
        for color in kmeans_colors:
            if not self.is_near_gray(color, gray_threshold):
                return np.clip(color, 0, 1)

        # If all colors are gray, return the first dominant shade
        return np.clip(kmeans_colors[0], 0, 1)

    def primary_color(self, k=4, gray_threshold=0.08):
        img_pixels = self.load_img_pixels()

        dom = self.dominant_color(img_pixels, k=k, gray_threshold=gray_threshold)

        return [ int(x * 255) for x in dom ] 

    def accent_color(self, k=8, gray_threshold=0.08, dom_compare_number=1):
        img_pixels = self.load_img_pixels()
        accents = self.extract_accents(img_pixels, k=k, gray_threshold=gray_threshold, dom_compare_number=dom_compare_number)

        return [int(x * 255) for x in accents[0]]

    def accent_colors(self, accent_number, k=8, gray_threshold=0.8, dom_compare_number=1):
        img_pixels = self.load_img_pixels()

        accents_raw = self.extract_accents(img_pixels, k=k, gray_threshold=gray_threshold, dom_compare_number=dom_compare_number)

        # Denormalizes the RGB values and casts them as ints
        out_accents = []
        for accent in accents_raw:
            out_accents.append([int(x * 255) for x in accent])

        # Repeats the accent colors until we have more than the requested value
        while len(out_accents) < accent_number:
            out_accents += out_accents

        # Returns exactly the rquested value of accent colors
        return out_accents[:accent_number]

    def dominant_colors(self, dom_number):
        img_pixels = self.load_img_pixels()

        colors_raw = self.extract_dominants(img_pixels, k=dom_number)

        out_doms = []
        for dom in colors_raw:
            out_doms.append([int(x * 255) for x in dom])

        return out_doms

    def test(self):
        img_pixels = self.load_img_pixels()
        # print(self.dominant_color(img_pixels))
        # self.get_kmeans(img_pixels)
        # print(self.extract_accents(img_pixels))
        # for i in range(0, 5):
        #     print(self.extract_accents(img_pixels, k=5, dom_compare_number=i))

        # self.display_img_accents(k=12, dom_compare_number=3)
        print(self.accent_color(img_pixels, k=12, dom_compare_number=2))

    def find_color_diff(self, rgb1, rgb2):
        rgb1 = sRGBColor(*rgb1)
        rgb2 = sRGBColor(*rgb2)

        lab1 = convert_color(rgb1, LabColor, target_illuminant="d65")
        lab2 = convert_color(rgb2, LabColor, target_illuminant="d65")

        delta_col = delta_e_cie2000(lab1, lab2)
        delta_L = abs(lab1.lab_l - lab2.lab_l)
        ab_distance = ((lab1.lab_a - lab2.lab_a) ** 2 + (lab1.lab_b - lab2.lab_b) ** 2) ** 0.5

        return {
                "col": delta_col,
                "l": delta_L,
                "ab": ab_distance
                }

    def format_rgb_output(self, rgb):
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}" 


    ########################## IMAGE PROCESSING METHODS #########################

    def get_kmeans(self, img_pixels, k=10):
        n_clusters = min(k, len(img_pixels))

        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=None)
        labels = kmeans.fit_predict(img_pixels)
        centers = kmeans.cluster_centers_

        counts = np.bincount(labels)
        sorted_indices = np.argsort(counts)[::-1]
    
        return centers[sorted_indices]

    def extract_accents(self, img_pixels, k=10, gray_threshold=0.08, dom_compare_number=1):
        kmeans_colors = self.get_kmeans(img_pixels, k=k)

        # dom_colors = list(kmeans_colors[0:dom_compare_number])
        dom_colors = [list(color) for color in kmeans_colors[0:dom_compare_number]]
        # accent_candidates = list(kmeans_colors[dom_compare_number:])
        accent_candidates = [list(accent) for accent in kmeans_colors[dom_compare_number:]]

        # Find the color difference of each color from the dominant colors
        color_differences = []
        for i, accent in enumerate(accent_candidates):
            color_diff = {"col": 0, "l":0, "ab":0} 
            for dom_color in dom_colors:
                diff = self.find_color_diff(accent, dom_color)

                # Add each difference to the sum
                color_diff["col"] += diff["col"]
                color_diff["l"] += diff["l"]
                color_diff["ab"] += diff["ab"]

            color_differences.append((accent, color_diff))

        # Filter out the colors that don't have enough color difference
        accents = []
        for color_pair in color_differences:
            if color_pair[1]["col"] > 20:
                accents.append(color_pair)

        # Sort the accents by color difference
        accents_sorted = sorted(accents, reverse=True, key=lambda a: a[1]["col"])
        # Get rid of the second dimention
        accents_sorted = [a[0] for a in accents_sorted]

        # Filter out the gray tones
        accents_no_gray = []
        for color in accents_sorted:
            if not self.is_near_gray(color, threshold=gray_threshold):
                accents_no_gray.append(color)

        # If there are no non-gray accents, just return the gray tones
        if len(accents_no_gray) == 0:
            return accents_sorted
        else:
            return accents_no_gray

    def extract_dominants(self, img_pixels, k=10, gray_threshold=0.08):
        colors = self.get_kmeans(img_pixels, k=k)

        return [list(color) for color in colors]


    ############################## IMAGE PLOTTING METHODS ######################

    def img_sub_plot(self, row, col, index, title, image):
        plt.subplot(row, col, index)
        plt.axis('off')
        plt.title(title)
        plt.imshow(image)

    def show_palette(self, row, col, index, title, colors):
        palette = np.zeros((50, 300, 3), dtype=np.uint8)
        step = 300 // len(colors)

        for i, color in enumerate(colors):
            palette[:, i * step:(i+1) * step] = color

        self.img_sub_plot(row, col, index, title, palette)

    def display_img_palette(self, n_colors=10):
        image = self.load_img_rgb()
        img_pixels = self.load_img_pixels()
        kmeans_cols = self.get_kmeans(img_pixels, k=n_colors) 

        colors = [[int(val * 255) for val in col] for col in kmeans_cols]

        self.img_sub_plot(2, 1, 1, os.path.basename(self.img_path), image)
        self.show_palette(2, 1, 2, "", colors)

        plt.show()

    def display_img_accents(self, k=10, dom_compare_number=1):
        image = self.load_img_rgb()
        img_pixels = self.load_img_pixels()

        accents = self.extract_accents(img_pixels, k=k, dom_compare_number=dom_compare_number)

        colors = [[int(val * 255) for val in col] for col in accents]

        self.img_sub_plot(2, 1, 1, os.path.basename(self.img_path), image)
        self.show_palette(2, 1, 2, "", colors)

        plt.show()


if __name__ == "__main__":
    usage_str = "Usage: python3 ColorPaletteEngine.py <image_path> [accent|dominant] <color_num>" 
    if len(sys.argv) != 4:
        print(usage_str)
        sys.exit(1)

    img_path = sys.argv[1]
    color_num = int(sys.argv[3])
    mode = sys.argv[2]

    engine = ColorPaletteEngine(img_path) 

    colors = []
    if mode == "accent":
        colors = engine.accent_colors(color_num, k=10, gray_threshold=0.10, dom_compare_number=3)
    elif mode == "dominant":
        colors = engine.dominant_colors(color_num)
    else:
        print(usage_str)
        sys.exit(1)

    for color in colors:
        print(engine.format_rgb_output(color))
    
