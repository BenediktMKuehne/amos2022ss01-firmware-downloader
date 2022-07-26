import os
import sys
import sqlite3
import unittest
import json
import inspect
from vendors.schneider_electric import download_single_file, write_metadata_to_db
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

class SchneiderUnitTest(unittest.TestCase):
    def setUp(self):
        setup_db()
        dest = DATA['file_paths']['download_test_files_path']
        if not os.path.isdir(dest):
            os.mkdir(dest)
        gt_file = "PM5560_PM5563_V2.7.4_Release.zip"  #Firmware_1.10.0_5500AC2.zip
        path = os.path.join(os.getcwd(), dest)
        self.gt_file_path = os.path.join(path, gt_file)
        self.gt_url = "https://download.schneider-electric.com/files?p_enDocType=Firmware&p_File_Name=PM5560_PM5563_V2.7.4_Release.zip&p_Doc_Ref=PM5560_PM5563_V2.7.4_Release"

    def test_download(self):
        dummy_data = {
            'Fwfileid': '',
            'Fwfilename': "",
            'Manufacturer': 'schneider_electric',
            'Modelname': "1.0.0",
            'Version': "1.0.0",
            'Type': "firmware",
            'Releasedate': "",
            'Checksum': '',
            'Filesize': '',
            'Lasteditdate': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': "https://test.com/firmware.zip",
            'Fwfilelinktolocal': self.gt_file_path,
            'Fwadddata': '',
            'Uploadedonembark': False,
            'Embarkfileid': '',
            'Startedanalysisonembark': False
        }
        print(self.gt_file_path)
        if os.path.exists(self.gt_file_path):
            os.remove(self.gt_file_path)
        download_single_file(self.gt_url, self.gt_file_path, dummy_data)
        self.assertTrue(os.path.exists(self.gt_file_path), msg="Path not exists")

    def test_if_data_entered_in_db(self):
        dummy_data = {
            'Fwfileid': '',
            'Fwfilename': "",
            'Manufacturer': 'schneider_electric',
            'Modelname': "1.0.0",
            'Version': "1.0.0",
            'Type': "firmware",
            'Releasedate': "",
            'Checksum': '',
            'Filesize': '',
            'Lasteditdate': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': "https://test.com/firmware.zip",
            'Fwfilelinktolocal': self.gt_file_path,
            'Fwadddata': '',
            'Uploadedonembark': False,
            'Embarkfileid': '',
            'Startedanalysisonembark': False
	}
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()
        select_command = "select * from FWDB WHERE Manufacturer='" + dummy_data["Manufacturer"] + "' AND Fwdownlink='" + dummy_data["Fwdownlink"] + "';"
        # Add data for schneider electric
        write_metadata_to_db([dummy_data])
        # Now test if one record exist for schneider_electric
        curs.execute(select_command)
        records = len(curs.fetchall())
        self.assertEqual(records, 1, msg="There should be only one record in db")

    def test_duplicate_data_check(self):
        dummy_data = {
            'Fwfileid': '',
            'Fwfilename': "",
            'Manufacturer': 'schneider_electric',
            'Modelname': "1.0.0",
            'Version': "1.0.0",
            'Type': "firmware",
            'Releasedate': "",
            'Checksum': '',
            'Filesize': '',
            'Lasteditdate': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': "https://test.com/firmware.zip",
            'Fwfilelinktolocal': self.gt_file_path,
            'Fwadddata': '',
            'Uploadedonembark': False,
            'Embarkfileid': '',
            'Startedanalysisonembark': False
        }
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()
        select_command = "select * from FWDB WHERE Manufacturer='" + dummy_data["Manufacturer"] + "' AND Fwdownlink='" + dummy_data["Fwdownlink"] + "';"
        # Add data for schneider electric
        write_metadata_to_db([dummy_data])
        # Now add same data multiple times to check if duplicates record exist or not with same download link
        write_metadata_to_db([dummy_data])
        write_metadata_to_db([dummy_data])
        write_metadata_to_db([dummy_data])
        # Now test if exactly one record exist for schneider_electric for this download link
        curs.execute(select_command)
        records = len(curs.fetchall())
        self.assertEqual(records, 1, msg="There should be only one record in db")


if __name__ == "__main__":
    unittest.main()
