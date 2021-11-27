import json
import os
import uuid

import numpy as np
import requests
import torch
from PIL import Image
from munch import Munch

TRANSLATION_PATH = "./data/translations"
INDEX_PATH = "./data/index"
COUNT_PATH = "./data/private/visits.txt"
WHICH_PATH = "./data/private/which.txt"
SENTENCE_DATA_PATH = './data/filelists/st_cmds_test_filelist.txt'
SLEEP_TIME = 5

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

def init_translation_data():
    if not os.path.exists(TRANSLATION_PATH):
        os.makedirs(TRANSLATION_PATH, exist_ok=True)
    
    dirs = os.listdir(TRANSLATION_PATH)
    return len(dirs)

def create_random_file_name():
    random_name = str(uuid.uuid4())
    return ''.join(random_name.split('-'))

def save_mp3_file(bytes, file_name):
    if not os.path.exists(TRANSLATION_PATH):
        os.makedirs(TRANSLATION_PATH, exist_ok=True)
    
    with open(os.path.join(TRANSLATION_PATH, file_name), 'wb') as file_out:
        file_out.write(bytes)
        print('Save to %s'%os.path.join(TRANSLATION_PATH, file_name))

def save_index_file(*args):
    if not os.path.exists(INDEX_PATH):
        os.makedirs(INDEX_PATH, exist_ok=True)
    
    next_sentence_file_name, next_sentence, file_name, gender, region, email, condition = args
    
    with open(os.path.join(INDEX_PATH, "index.txt"), 'a') as file_out:
        file_out.write("|".join(list(args)) + "\n")

def load_filepaths_and_text(filename, split=" | "):
    with open(filename, encoding='utf-8') as f:
        filepaths_and_text = [line.strip().split(split) for line in f]
    return filepaths_and_text
    

def base_count_init(PATH):
    parent_dir = os.path.dirname(os.path.realpath(PATH))
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    
    if not os.path.exists(PATH):
        with open(PATH, 'w') as file_out:
            file_out.write("0")
       
    with open(PATH, 'r') as file_in:
        n_visits = file_in.readline().strip('\n').strip(" ")
        n_visits = int(n_visits)
        
    return n_visits

def init_visits():
    return base_count_init(COUNT_PATH)

def init_sentence_data():
    lists = load_filepaths_and_text(SENTENCE_DATA_PATH)
    return base_count_init(WHICH_PATH), lists 

def pt_cs_translator_init():
    count_visits = init_visits()
    count_translations = init_translation_data()
    which_sentence_idx, sentence_list = init_sentence_data()
    return count_visits, count_translations, which_sentence_idx, sentence_list
            
def easy_save_count(which_one, file_name):
    with open(file_name, 'w') as file_out:
            file_out.write(str(which_one))
            
def get_count_translations():
    return len(os.listdir(TRANSLATION_PATH))