import os
import sys
import sqlite3
import inspect
from utils.database import Database
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.abspath(os.path.join('.', '')))

#check duplicate data for firmware web scrapping
def check_duplicates(firmware_data, db_name):
    db_ = Database()
    db_.db_check()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute("select * from FWDB WHERE Manufacturer='" + firmware_data["Manufacturer"] + "' AND Modelname='" + firmware_data["Modelname"] + "' AND Version = '" + firmware_data["Version"] + "'")
    except sqlite3.Error as er_:
        print('SQLite error: %s' % (' '.join(er_.args)))
        return False

    data_list = cursor.fetchall()
    conn.close()

    return len(data_list) > 0
