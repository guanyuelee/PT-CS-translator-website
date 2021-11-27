import sqlite3 as sqlite

DATABASE_FILE = "PT_CS_Dataset.db"
TABLE_NAME = "ALL_PT_TEXT"
TABLE_TRANS = "TRANSLATION"
TABLE_VISITS = 'VISITS'

def get_one_pt_text(cursor, connection):
    cursor.execute("SELECT * FROM %s WHERE TRANSLATED == 0 AND SENT == 0 LIMIT 1" % (TABLE_NAME))
    data = cursor.fetchone()
    if data is not None:
        id, filename, text, _, _, _ = data
        cursor.execute("UPDATE %s SET SENT=1 WHERE ID==%d" % (TABLE_NAME, id))
        connection.commit()
        return (id, filename, text)
    else:
        return None

def check_is_valid(cursor, id):
    cursor.execute("SELECT * FROM %s WHERE ID==%d" % (TABLE_NAME, id))
    data = cursor.fetchone()
    if data is not None:
        id, _, _, is_translated, _, _ = data
        if is_translated == 1:
            return False
        else:
            return True
    else:
        return False

def update_database_when_received(cursor, connection, id):
    cursor.execute("UPDATE %s SET TRANSLATED=1 WHERE ID==%d" % (TABLE_NAME, id))
    connection.commit()
    
def update_database_periodically(cursor, connection, expire_time):
    cursor.execute("UPDATE %s SET SENT_TIME = SENT_TIME + 1 WHERE ID IN (SELECT ID FROM %s WHERE SENT=1 AND TRANSLATED=0)" % 
                   (TABLE_NAME, TABLE_NAME))
    connection.commit()
    cursor.execute("UPDATE %s SET SENT=0, SENT_TIME=0 WHERE ID IN (SELECT ID FROM %s WHERE SENT_TIME > %d)" % 
                   (TABLE_NAME, TABLE_NAME, expire_time))
    connection.commit()
    
def insert_translation(cursor, connection, id, gender, region, email, condition, pt_text, pt_file, cs_file, pt_id):
    cursor.execute("INSERT INTO %s VALUES (%d, \'%s\', \'%s\', \'%s\', %d, \'%s\', \'%s\', \'%s\', %d)" % 
                   (TABLE_TRANS, id, gender, region, email, condition, pt_text, pt_file, cs_file, pt_id))
    connection.commit()
    
def get_translation_count(cursor):
    cursor.execute("SELECT COUNT(*) FROM %s" % (TABLE_TRANS))
    n_counts = cursor.fetchone()[0]
    return n_counts

def get_visits_count(cursor, model):
    cursor.execute("SELECT COUNT(*) FROM %s WHERE MODEL=\'%s\'" % (TABLE_VISITS, model))
    n_counts = cursor.fetchone()[0]
    return n_counts

def get_all_visits_count(cursor):
    cursor.execute("SELECT COUNT(*) FROM %s" % (TABLE_VISITS))
    n_counts = cursor.fetchone()[0]
    return n_counts

def insert_visits_count(cursor, connection, id, model):
    print("INSERT INTO %s VALUES (%d, \'%s\')" % (TABLE_VISITS, id, model))
    cursor.execute("INSERT INTO %s VALUES (%d, \'%s\')" % (TABLE_VISITS, id, model))
    connection.commit()
    
    

