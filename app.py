from sqlite3.dbapi2 import SQLITE_UPDATE
import werkzeug
from flask import Flask, render_template, send_from_directory, request
from munch import Munch
import numpy as np
import _thread
import os
import time
import sqlite3 as sqlite

from models import StarGANv2
from utils import load_cfg, cache_path, data_path, create_random_file_name, save_mp3_file
from utils import SLEEP_TIME

from database_utils import *

cfg = load_cfg()
app = Flask(__name__)

def save_count_visits():
    while True:
        time.sleep(SLEEP_TIME)   # 5 sec
        connection = sqlite.connect(DATABASE_FILE)
        cursor = connection.cursor()
        update_database_periodically(cursor, connection, expire_time=20)   # a connection that is not respended for over 300s will be reset.
        connection.close() 

try:
    _thread.start_new_thread(save_count_visits, (), )
except:
    print("Error: unable to start thread")

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
    if model_id in cfg.models:
        connection = sqlite.connect(DATABASE_FILE)
        cursor = connection.cursor()
        model = cfg.models[model_id]
        n_visits = get_all_visits_count(cursor)
        insert_visits_count(cursor, connection, n_visits + 1, model_id)
        all_page_visits = get_visits_count(cursor, model_id)
        trans_count = get_translation_count(cursor)
        connection.close()
        return render_template(f'{model_id}.html', title=model['name'], description=model['description'], 
                               description_en=model["description_en"], 
                               count_visits=all_page_visits, 
                               count_translations=trans_count)
    else:
        return render_template('index.html', message=f'No such model: {model_id}.', is_warning=True)


@app.route('/api/model', methods=['POST'])
def model_inference():
    res = Munch({
        "success": False,
        "message": "default message",
        "data": None
    })
    try:
        model_name = request.form['model']
        if model_name == 'starganv2_afhq':
            res = StarGANv2.controller(request)
        else:
            res.message = f"no such model: {model_name}"
    except Exception as e:
        res.message = str(e)
        print(e)
    return res

@app.route('/api/upload', methods=['POST'])
def upload():
    print("#####################", time.time(), "#####################")
    res = Munch({
        "success": False,
        "next_sentence": None,
        "next_sentence_file_name": None, 
        "which_sentence": None, 
        "count_translations": 0,
        "message": "我们已经翻译完毕了！感谢您的付出！请看顶部我们收集了多少翻译。", 
        "isEnd": False
    })
    
    try:
        # save data
        connection = sqlite.connect(DATABASE_FILE)
        cursor = connection.cursor()
        print("Note: We have linked the database successfully. ")
        is_next = True if int(request.form['next_is_click']) else False
        print("Note: The use click \'is_next\'=", is_next)
        
        if not is_next:
            print("Note: Save the data!")
            gender = request.form["gender"]
            n_translations = int(request.form["n_translations"])  # The order of sentence that user translates. 
            region = request.form['region']
            email = request.form["email"]
            condition = 1 if request.form["condition"] else 0
            next_sentence = request.form["next_sentence"]
            next_sentence_file_name = request.form["next_sentence_file_name"]
            which_sentence = int(request.form["which_sentence"])
            
            if n_translations != 0:
                is_valid = check_is_valid(cursor, which_sentence)
                if is_valid:
                    update_database_when_received(cursor, connection, which_sentence)
                    id = get_translation_count(cursor) + 1
                    # if not testing sentence, just ignore. 
                    file_name = create_random_file_name() + ".mp3"
                    bytes = request.files['upfile'].read()
                    save_mp3_file(bytes, file_name)
                    insert_translation(cursor, connection, id, gender, region, email, condition, pt_text=next_sentence, 
                                    pt_file=next_sentence_file_name, cs_file=file_name, pt_id=which_sentence)
        
        print("Note: Fetch new data!")
        # respond next sentence. 
        data = get_one_pt_text(cursor, connection)
        print("Note: new data is ", data)
        if data is not None:
            which_sentence, next_sentence_file_name, next_sentence = data
            res.which_sentence = which_sentence
            res.next_sentence_file_name = next_sentence_file_name
            res.next_sentence = next_sentence
            res.count_translations = get_translation_count(cursor)
            res.success = True
        else:
            res.count_translations = get_translation_count(cursor)
            res.success = True
            res.isEnd = True
            
        connection.close()
        
    except Exception as e:
        res.message = str(e)
        print("Error: ", e)
    
    print("^^^^^^^^^^^^^^^^^^^^^^^", time.time(), "^^^^^^^^^^^^^^^^^^^^^^^^^")
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

# StarGANv2.init(cfg.device)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=cfg.port)
