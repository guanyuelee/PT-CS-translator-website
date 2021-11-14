import werkzeug
from flask import Flask, render_template, send_from_directory, request
from munch import Munch
import numpy as np
import _thread
import os
import time

from models import StarGANv2
from utils import init_visits, load_cfg, cache_path, init_translation_data

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
    global count_translations
    
    count_visits += 1
    if model_id in cfg.models:
        model = cfg.models[model_id]
        return render_template(f'{model_id}.html', title=model['name'], description=model['description'], description_en=model["description_en"], 
                               count_visits=count_visits, count_translations=count_translations)
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
        "next_sentence": "Please translate: I received your message. ",
        "data": None
    })
    print("I received 2")
    try:
        f = request.files['upfile']
        data = f.read()
        with open('test.mp3', 'wb') as file_out:
            file_out.write(data)
        
    except Exception as e:
        res.message = str(e)
        print(e)
        
    return res  


@app.route('/cache/<path:filename>')
def cached_image(filename):
    return send_from_directory(cache_path, filename)


@app.route('/api/<model_name>', methods=['POST'])
def predict(model_name):
    return {
        "success": True,
        "message": model_name
    }
       
 
StarGANv2.init(cfg.device)

def save_count_visits():
    file_name = 'visits.txt'
    path = "./data/private"
    while True:
        time.sleep(10)
        with open(os.path.join(path, file_name), 'w') as file_out:
            file_out.write(str(count_visits))
            
count_visits = init_visits()
cur_translation_list, count_translations = init_translation_data()
    
try:
    _thread.start_new_thread(save_count_visits, (), )
except:
    print("Error: unable to start thread")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=cfg.port)
