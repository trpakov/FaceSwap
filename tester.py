from pickletools import optimize
import cv2, os, glob
from backend.swapper import Swapper
from PIL import Image
import numpy as np
from subprocess import call
import requests
from io import BytesIO

# img1 = open(r"D:\Documents\SimSwap\1.jpg", 'rb').read()
# img2 = open(r"D:\Documents\SimSwap\2.jpg", 'rb').read()
# img3 = open(r"C:\Users\TrPakov\Pictures\vlcsnap-5560-11-06-18h01m32s177.png", 'rb').read()
# img4 = open(r"C:\Users\TrPakov\Pictures\11999036_1059778260712467_2103780466503895976_n.jpg", 'rb').read()


# swapper = Swapper(use_cache=True)
# result = swapper.swap(img1, img2)
# # result = swapper.swap(img1, img2)
# cv2.imshow('test', result)
# # result2 = swapper.swap(img1, img3, mode='multi')
# # cv2.imshow('test2', result2)
# swapper.save_cache()
# cv2.waitKey()
# print('done')

# path = os.path.join('backend/temp', '*.png')
# image_filenames = sorted(glob.glob(path))
# img, *imgs = [Image.open(f) for f in image_filenames]

# img.save('test2.gif', format='GIF', append_images=imgs,
#         save_all=True, duration=200, loop=0)

# print(cm)
# call(cm)

# dest = requests.get('https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/1200px-Image_created_with_a_mobile_phone.png', allow_redirects=True).content
# dest_np = np.frombuffer(dest, np.uint8)
# dest_img = cv2.imdecode(dest_np, cv2.IMREAD_COLOR)
# cv2.imshow('te', dest_img)
# cv2.waitKey()

# url = glob.glob('backend/results/1af32cdf14ba490f8648c53c84f165a3.*')
# print(url[0])

img1 = open(r"D:\Documents\SimSwap\1.jpg", 'rb').read()
img2 = open(r"D:\Documents\SimSwap\9hgC.gif", 'rb').read()
swapper = Swapper(use_cache=False)
result = swapper.swap_gif(img1, img2, ext='gif')
print(result)