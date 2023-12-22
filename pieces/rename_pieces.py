import os
from tqdm import tqdm
from PIL import Image

pieces = ["bb", "bk", "bn", "bq", "br", "wb", "wk", "wn", "wp", "wq", "wr"]

for folder in tqdm(os.listdir("imgs/pieces")):
    for image in os.listdir(f"imgs/pieces/{folder}"):
        new_name = f"imgs/pieces/{folder}/{image[0] + (image[1].upper() if image[1] != 'p' else image[1])}.png"
        old_name = f"imgs/pieces/{folder}/{image}"

        img = Image.open(old_name)
        new_image = img.resize((60, 60))
        new_image.save(old_name)

        os.rename(old_name, new_name)
