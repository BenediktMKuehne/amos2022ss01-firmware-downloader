import os
import json
import sqlite3
import requests
from bs4 import BeautifulSoup
from utils.database import Database
from utils.Logs import get_logger

logger = get_logger("upload.upload")
CONFIG_PATH = os.path.join("config", "config.json")
DATA={}
with open(CONFIG_PATH, "rb") as fp:
    DATA = json.load(fp)

class FirmwareUploader:
    def __init__(self):
        self.auth_url = DATA['uploader']['auth_url']
        self.upload_fw_url = DATA['uploader']['upload_fw_url']
        self.start_analysis_url = DATA['uploader']['start_analysis_url']
        self.cookies = {}

    def authenticate(self, username, password):
        resp = requests.get(self.auth_url)
        for cookie in resp.cookies:
            self.cookies[cookie.name] = cookie.value
        data =  {
            "csrfmiddlewaretoken": self.cookies.get("csrftoken", ""),
            "username": username,
            "password": password
        }
        resp = requests.post(self.auth_url,  data=data, cookies=self.cookies, allow_redirects=False)
        for cookie in resp.cookies:
            self.cookies[cookie.name] = cookie.value #saving csrftoken and seesionid cookies
        if set(["csrftoken", "sessionid"]).issubset(self.cookies.keys()):
            logger.info("authentication is successful")
        else:
            logger.error("authentication failed")
        logger.info(self.cookies)

    def start_fw_analysis(self, fw_):
        data = {
            "csrfmiddlewaretoken": self.cookies.get("csrftoken", None),
            "firmware": fw_['id'],
            "version": fw_['version'],
            "vendor": fw_['vendor'],
            "device": "",
            "notes": "",
            "firmware_Architecture": "",
            "grep_able_log": "on",
            "relative_paths": "on",
            "ANSI_color": "on",
            "web_reporter": "on",
            "emulation_test": "on",
            "dependency_check": "on",
            "multi_threaded": "on",
            "firmware_remove": "on"
        }
        resp = requests.post(self.start_analysis_url, data=data, cookies=self.cookies)
        if resp.status_code == 200:
            logger.info("Started firmware analysis successfully")
            return True
        else:
            logger.error("Failed to start firmware analysis")
            return False

    def upload_fw(self, fw_):
        with open(fw_, 'rb') as firmware_file:
            files = [('file', firmware_file)]
            headers = {
                "X-CSRFToken": self.cookies.get('csrftoken', "")
            }
            resp = requests.post(self.upload_fw_url, files=files, headers=headers, cookies=self.cookies, allow_redirects=False)
            if resp.content == b'successful upload':
                logger.info("File is uploaded successfully")
                return True
            else:
                return False

    def get_id_of_uploaded_file(self, filename):
        req = requests.get(self.start_analysis_url, cookies=self.cookies)
        soup = BeautifulSoup(req.text, 'html.parser')
        items = soup.find_all("select", id="id_firmware")
        options = items[0].find_all("option")
        for item in options:
            scrapped_filename = item.decode_contents().split("- ")[-1]
            scrapped_id = item.get("value")
            if "selected" in item.attrs.keys():
                if scrapped_filename == filename.replace(" ", "_"):
                    logger.info("Found id of uploaded file %s", scrapped_id)
                    return scrapped_id

        logger.error("Id not found for filename %s", filename)
        return None

    def analysis(self, db_name):
        db_ = Database()
        db_.db_check()
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("select * from FWDB WHERE Uploadedonembark=1 AND Startedanalysisonembark=''")
            data_list_1 = cursor.fetchall()
            for file in data_list_1:
                if file[17]:
                    fw_metadata_1 = {
                        'id': file[17],
                        'version': file[4],
                        'vendor': file[2]
                    }
                    is_analysis_start = self.start_fw_analysis(fw_metadata_1)
                    if is_analysis_start is True:
                        cursor.execute('''UPDATE FWDB SET Startedanalysisonembark = ? WHERE Fwfileid = ?''', (is_analysis_start, file[0]))
                        conn.commit()

        except sqlite3.Error as er_:
            logger.error('SQLite error: %s', (' '.join(er_.args)))

        conn.close()

    def anaylise_data_file(self, db_name):
        db_ = Database()
        db_.db_check()
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("select * from FWDB WHERE Uploadedonembark=''")
            data_list = cursor.fetchall()
            self.authenticate(DATA['uploader']['username'], DATA['uploader']['password'])
            fw_metadata = {}
            for file in data_list:
                if file[14]:
                    fw_metadata["file_path"] = file[14]
                    is_fw_uploaded = self.upload_fw(fw_metadata["file_path"])
                    fw_metadata["id"] = self.get_id_of_uploaded_file(file[1])
                    fw_metadata["version"] = file[4]
                    fw_metadata["vendor"] = file[2]
                    if is_fw_uploaded is True:
                        cursor.execute('''UPDATE FWDB SET Uploadedonembark = ? WHERE Fwfileid = ?''', (is_fw_uploaded, file[0]))
                        conn.commit()
                        if fw_metadata["id"] is not None:
                            cursor.execute('''UPDATE FWDB SET Embarkfileid = ? WHERE Fwfileid = ?''', (fw_metadata["id"], file[0]))
                            conn.commit()
            conn.close()
            self.analysis(db_name)

        except sqlite3.Error as er_:
            logger.error('SQLite error: %s', (' '.join(er_.args)))
