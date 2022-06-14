import os
import sqlite3
from ge import *
from database import Database
import unittest
from check_duplicates import check_duplicates

def fetch_data(modelname):
    db = Database(dbname=db_name)
    if db_name not in os.listdir('.'):
        db.create_table()
    #db connection
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute("select * from FWDB WHERE Manufacturer='GE' and Modelname='"+modelname+"'")
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))

    def test_case_without_authentication(self):
        data = ["orbit-mib-9_2_2.zip", "2022-05-12"]
        folder = 'File_system'
        file_name = 'orbit-mib-9_2_2.zip'
        gt_url = "https://www.gegridsolutions.com/communications/mds/software.asp?directory=Orbit_MCR&file=orbit%2Dmib%2D9%5F2%5F2%2Ezip"
        dest = os.path.join(os.getcwd(), folder)
        try:
            if not os.path.isdir(dest):
                os.mkdir(dest)

class Unit_Case_Test(unittest.TestCase):
    def test_case_without_authentication(self):
        data = ["orbit-mib-9_2_2.zip", "2022-05-12"]
        folder = 'File_system'
        file_name = 'orbit-mib-9_2_2.zip'
        gt_url = "https://www.gegridsolutions.com/communications/mds/software.asp?directory=Orbit_MCR&file=orbit%2Dmib%2D9%5F2%5F2%2Ezip"
        dest = os.path.join(os.getcwd() ,folder)
        try:
            if not os.path.isdir(dest):
                os.mkdir(dest)
        except Exception as e:
            raise ValueError(f"{e}")
        gt_file_path = os.path.join(dest, file_name)
        download_file(gt_url, gt_file_path, data[0], data[1], folder, file_name, '', '', '')
        data = {
            'Manufacturer': 'GE',
            'Modelname': file_name,
            'Version': '',
	    }
        
        self.assertTrue(check_duplicates(data, 'firmwaredatabase.db'), msg="Image didn't downloaded")
        fetch_data(file_name)
        

    def test_case_with_authentication(self):
        data = ["SDx-6_4_8.mpk", "2022-03-29"]
        folder = 'File_system'
        file_name = 'SDx-6_4_8.mpk'
        gt_url = "https://www.gegridsolutions.com/communications/mds/software.asp?directory=SD_Series"
        dest = os.path.join(os.getcwd() ,"test_files")
        try:
            if not os.path.isdir(dest):
                os.mkdir(dest)
        except Exception as e:
            raise ValueError(f"{e}")
        gt_file_path = os.path.join(dest, file_name)
        download_file(gt_url, gt_file_path, data[0], data[1], folder, file_name, 'javascript:;', gt_url, "Passport_DownloadFile('SDSeries',7,70);return false")
        data = {
            'Manufacturer': 'GE',
            'Modelname': file_name,
            'Version': '',
	    }
        
        self.assertTrue(check_duplicates(data, 'firmwaredatabase.db'), msg="Image didn't downloaded")
        fetch_data(file_name)

if __name__=="__main__":
    unittest.main()