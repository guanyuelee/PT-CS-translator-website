import json
import os
import uuid

import numpy as np
import requests
import torch
from PIL import Image
from munch import Munch


def load_cfg(cfg_path="config.json"):
    assert os.path.exists(cfg_path), "config.json is missing!"
    with open(cfg_path, 'rb') as f:
        cfg = json.load(f)
    cfg = Munch(cfg)
    return cfg


data_path = './data'
cache_path = 'cache'


def load_weights(file_name, download_url, device):
    os.makedirs(data_path, exist_ok=True)
    weight_path = os.path.join(data_path, file_name)
    if not os.path.exists(weight_path):
        print(f"Downloading from: {download_url}...")
        res = requests.get(download_url)
        with open(weight_path, 'wb') as f:
            f.write(res.content)
        print(f'File saved at: {weight_path}')
    return torch.load(weight_path, map_location=torch.device(device))


def set_eval_mode(nets):
    for net in nets.values():
        net.eval()


def to_device(nets, device):
    for net in nets.values():
        net.to(device)


def denormalize(x):
    out = (x + 1) / 2
    return out.clamp_(0, 1)


def get_image_name():
    return f"{uuid.uuid4().hex}.png"


def save_images(imgs):
    imgs = denormalize(imgs)
    imgs = imgs * 255
    imgs = imgs.cpu().numpy().astype(np.uint8)
    imgs = imgs.transpose((0, 2, 3, 1))
    os.makedirs(cache_path, exist_ok=True)
    filenames = []
    for img in imgs:
        img = Image.fromarray(img)
        filename = os.path.join(cache_path, get_image_name()).replace("\\", "/")
        img.save(filename)
        filenames.append(filename)
    return filenames

file_name = 'visits.txt'
path = "./data/private"

def init_visits():
    if not os.path.exists(os.path.join(path, file_name)):
        with open(os.path.join(path, file_name), 'w') as file_out:
            file_out.write("0")
    
    with open(os.path.join(path, file_name), 'r') as file_in:
        n_visits = file_in.readline().strip('\n').strip(" ")
        n_visits = int(n_visits)
        
    return n_visits

def init_translation_data():

    path = "./data/translation"
    dirs = os.listdir(path)
    return dirs, len(dirs)


        
