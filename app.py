import werkzeug
from flask import Flask, render_template, send_from_directory, request
from munch import Munch
import numpy as np
import _thread
import os
import time

from models import StarGANv2
from utils import WHICH_PATH, load_cfg, cache_path, data_path, create_random_file_name, save_mp3_file, save_index_file, pt_cs_translator_init,\
    easy_save_count, get_count_translations
from utils import COUNT_PATH, SLEEP_TIME, WHICH_PATH

cfg = load_cfg()
app = Flask(__name__)
total_targets = []
cur_translation_list = []

count_translations = 0
count_visits = 0

@app.context_processor
def inject_config():
    return dict(cfg=cfg)


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/model/<model_id>', methods=['GET'])
def model_page(model_id):
    global count_visits
    
    count_visits += 1
    if model_id in cfg.models:
        model = cfg.models[model_id]
        return render_template(f'{model_id}.html', title=model['name'], description=model['description'], description_en=model["description_en"], 
                               count_visits=count_visits, count_translations=get_count_translations())
    else:
        return render_template('index.html', message=f'No such model: {model_id}.', is_warning=True)


@app.route('/api/model', methods=['POST'])
def model_inference():
    res = Munch({
        "success": False,
        "message": "default message",
        "data": None
    })
    print("I receive!")
    try:
        model_name = request.form['model']
        if model_name == 'starganv2_afhq':
            res = StarGANv2.controller(request)
        elif model_name == 'pt_cs_translator':
            res = StarGANv2.controller(request)
        else:
            res.message = f"no such model: {model_name}"
    except Exception as e:
        res.message = str(e)
        print(e)
    return res

@app.route('/api/upload', methods=['POST'])
def upload():
    res = Munch({
        "success": False,
        "next_sentence": None,
        "next_sentence_file_name": None, 
        "which_sentence": None, 
        "count_translations": 0
    })
    
    try:
        # save data
        gender = request.form["gender"]
        n_translations = int(request.form["n_translations"])  # The order of sentence that user translates. 
        region = request.form['region']
        email = request.form["email"]
        condition = request.form["condition"]
        next_sentence = request.form["next_sentence"]
        next_sentence_file_name = request.form["next_sentence_file_name"]
        
        if n_translations != 0:
            # if not testing sentence, just ignore. 
            file_name = create_random_file_name() + ".mp3"
            bytes = request.files['upfile'].read()
            save_mp3_file(bytes, file_name)
            save_index_file(next_sentence_file_name, next_sentence, file_name, gender, region, email, condition)
            print(f"{n_translations}")
        
        # respond next sentence. 
        global which_sentence
        which_sentence += 1
        res.which_sentence = which_sentence
        res.which_sentence = which_sentence
        res.next_sentence_file_name = sentence_lists[res.which_sentence % N_SENTENCES][0]
        res.next_sentence = sentence_lists[res.which_sentence % N_SENTENCES][1]
        res.count_translations = get_count_translations()
        res.success = True
        
    except Exception as e:
        res.message = str(e)
        print(e)
        
    return res  


@app.route('/cache/<path:filename>')
def cached_image(filename):
    return send_from_directory(cache_path, filename)

@app.route('/data/<path:filename>')
def data_controller(filename):
    return send_from_directory(data_path, filename)


@app.route('/api/<model_name>', methods=['POST'])
def predict(model_name):
    return {
        "success": True,
        "message": model_name
    }

StarGANv2.init(cfg.device)

count_visits, count_translations, which_sentence, sentence_lists = pt_cs_translator_init()
N_SENTENCES = len(sentence_lists)

def save_count_visits():
    while True:
        time.sleep(SLEEP_TIME)
        easy_save_count(count_visits, file_name=COUNT_PATH)
        easy_save_count(which_sentence, file_name=WHICH_PATH)
    
try:
    _thread.start_new_thread(save_count_visits, (), )
except:
    print("Error: unable to start thread")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=cfg.port)
