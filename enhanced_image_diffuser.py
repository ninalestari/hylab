import requests
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionUpscalePipeline
import torch

# load model and scheduler
model_id = "CompVis/stable-diffusion-v1-4-lite"
pipeline = StableDiffusionUpscalePipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipeline = pipeline.to("cuda")

def get_low_res_img(url, shape):
    response = requests.get(url)
    low_res_img = Image.open(BytesIO(response.content)).convert("RGB")
    low_res_img = low_res_img.resize(shape)
    return low_res_img

url = "https://cdn.pixabay.com/photo/2017/02/07/16/47/kingfisher-2046453_640.jpg"
shape = (200, 128)
low_res_img = get_low_res_img(url, shape)
low_res_img
"""
Generates an upscaled image based on the provided prompt and low-resolution image.

Args:
    prompt (str): The prompt to use for generating the upscaled image.
    low_res_img (PIL.Image): The low-resolution image to upscale.

Returns:
    PIL.Image: The upscaled image.
"""
'''
prompt = "an aesthetic kingfisher"
upscaled_image = pipeline(prompt=prompt, image=low_res_img).images[0]
upscaled_image
'''
prompt = "an aesthetic kingfisher, UHD, 4k, hyper realistic, extremely detailed, professional, vibrant, not grainy, smooth"
upscaled_image = pipeline(prompt=prompt, image=low_res_img).images[0]
upscaled_image
