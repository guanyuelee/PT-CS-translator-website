import sqlite3 as sqlite
import os
import sys

filelists_path = "./data/filelists/st_cmds_all_filelist.txt"

def load_filepaths_and_text(filename, split=" | "):
    with open(filename, encoding='utf-8') as f:
        filepaths_and_text = [line.strip().split(split) for line in f]
    return filepaths_and_text

def insert_line_into_sql(cursor, id, path, text, translated, sent, sent_time):
    path = path.split("/")[-1]
    command = "INSERT INTO ALL_PT_TEXT VALUES (%d, \'%s\', \'%s\', %d, %d, %d)" % (id, path, text, translated, sent, sent_time)
    cursor.execute(command)
    
def display_database(cursor):
    command = "SELECT * FROM ALL_PT_TEXT"
    cursor.execute(command)
    data = cursor.fetchall()
    for row in data:
        print(f"{row[0], row[1], row[2]}")

filepaths_and_text = load_filepaths_and_text(filelists_path)

con = None
try:
    con = sqlite.connect("PT_CS_Dataset.db")
    cur = con.cursor()
    cur.execute("SELECT SQLITE_VERSION()")
    data = cur.fetchone()[0]
    print(f"SQLite version: {data}")
    
    for i in range(len(filepaths_and_text)):
        insert_line_into_sql(cur, i+1, filepaths_and_text[i][0], filepaths_and_text[i][1], 0, 0, 0)
    
    con.commit()

except sqlite.Error as e:
    print(f"Error {e.args[0]}")
    sys.exit(1)
    