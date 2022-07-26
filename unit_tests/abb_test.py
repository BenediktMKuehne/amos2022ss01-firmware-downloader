import os
import sys
import sqlite3
import unittest
import json
import inspect
from vendors.abb import download_single_file, write_metadata_to_db
from utils.check_duplicates import Database
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.abspath(os.path.join('.', '')))

DB_NAME = "firmwaredatabase.db"
CONFIG_PATH = os.path.join(parent_dir, "config", "config.json")
DATA={}
with open(CONFIG_PATH, "rb") as fp:
    DATA = json.load(fp)

def setup_db():
    db_ = Database()
    db_.db_check()
    db_.create_table()

def fetch_data():
    db_ = Database()
    db_.db_check()
    # db connection
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("select * from FWDB WHERE Manufacturer='abb'")
    except sqlite3.Error as er_:
        print('SQLite error:%s' % (' '.join(er_.args)))

    data_list = cursor.fetchall()
    print(data_list)
    conn.close()


class ABBUnitTest(unittest.TestCase):
    def setUp(self):
        setup_db()
        self.dest = DATA['file_paths']['download_test_files_path']
        if not os.path.isdir(self.dest):
            os.mkdir(self.dest)
        self.gt_file = "Liquid_Metric_Master_5.0.0_2runs.fxm"  #Firmware_1.10.0_5500AC2.zip
        path = os.path.join(os.getcwd(), self.dest)
        # self.gt_file_path = path
        self.gt_file_path = os.path.join(path, self.gt_file)
        self.gt_url = "https://search.abb.com/library/Download.aspx?DocumentID=SW%2fFlowX%2fLM_5.0.0_2s&LanguageCode=en&DocumentPartId=&Action=Launch&DocumentRevisionId=A"
        self.dummy_data = {
            'Fwfileid': '',
            'Fwfilename': self.gt_file,
            'Manufacturer': 'abb',
            'Modelname': 'SW/FlowX/LM_5.0.0_2s',
            'Version': 'A',
            'Type': 'Software',
            'Releasedate': '2022-07-20T10:55:00.997Z',
            'Filesize': '',
            'Lasteditdate': '',
            'Checksum': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': self.gt_url,
            'Fwfilelinktolocal': os.path.abspath(self.dest),
            # setting temp filename as of now
            'Fwadddata': '{"summary": "Software - Spirit IT Flow-Xpress - Liquid Metric Application with max. 2 streams per flow computer"}',
            'Uploadedonembark': False,
            'Embarkfileid': '',
            'Startedanalysisonembark': False
        }

    def test_download(self):
        print(self.gt_file_path)
        if os.path.exists(self.gt_file_path):
            os.remove(self.gt_file_path)
        download_single_file(self.dummy_data, self.dest)
        self.assertTrue(os.path.exists(self.gt_file_path), msg="Path not exists")

    def test_if_data_entered_in_db(self):
        dummy_data = self.dummy_data
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()
        select_command = "select * from FWDB WHERE Manufacturer='" + dummy_data["Manufacturer"] + "' AND Fwdownlink='" + \
                         dummy_data["Fwdownlink"] + "';"
        # Add data for schneider electric
        write_metadata_to_db([dummy_data])
        # Now test if one record exist for abb
        curs.execute(select_command)
        records = len(curs.fetchall())
        self.assertEqual(records, 1, msg="There should be only one record in db")

    def test_for_check_dublicates(self):
        dummy_data = self.dummy_data
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()
        select_command = "select * from FWDB WHERE Manufacturer='" + dummy_data["Manufacturer"] + "' AND Fwdownlink='" + \
                         dummy_data["Fwdownlink"] + "';"
        # Add data for schneider electric
        write_metadata_to_db([dummy_data])
        # Now add same data multiple times to check if duplicates record exist or not with same download link
        write_metadata_to_db([dummy_data])
        write_metadata_to_db([dummy_data])
        write_metadata_to_db([dummy_data])
        # Now test if exactly one record exist for abb for this download link
        curs.execute(select_command)
        records = len(curs.fetchall())
        self.assertEqual(records, 1, msg="There should be only one record in db")


if __name__ == "__main__":
    unittest.main()
