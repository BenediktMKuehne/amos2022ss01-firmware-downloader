import os
import sys
import json
import math
import uuid
from urllib.parse import urlparse
import inspect
from datetime import datetime
import requests
from utils.database import Database
from utils.Logs import get_logger
from utils.modules_check import vendor_field
from utils.metadata_extractor import get_hash_value, metadata_extractor
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


sys.path.append(os.path.abspath(os.path.join('.', '')))

MOD_NAME = "abb"
logger = get_logger("vendors.abb")
CONFIG_PATH = os.path.join(parent_dir, "config", "config.json")
DATA={}
URL = ''

SKIP_FILES = ["pdf", "txt"]

with open(CONFIG_PATH, "rb") as fp:
    DATA = json.load(fp)

    if vendor_field('abb', 'url') is False:
        print('error url')
        logger.error('<module : abb > -> url not present')
        URL = "https://discoveryapi.library.abb.com/api/public/documents"
    else:
        # print(' url')
        URL = vendor_field('abb', 'url')


def download_single_file(file_metadata, folder):
    url = file_metadata["Fwdownlink"]
    logger.debug('<module ABB> -> Downloading Firmware <%s> <%s>', file_metadata['Fwfilename'], file_metadata['Version'])
    logger.debug('<Module ABB> -> Downloading Firmware From Web page <%s>', url)
    resp = requests.get(url, allow_redirects=True)
    if resp.status_code != 200:
        logger.error('<%s> is invalid', url)
        raise ValueError('<%s> is invalid' % url)
    final_obj_url = resp.request.url
    file_name = urlparse(final_obj_url).path.split("/")[-1].replace("%20", " ")
    old_file_name_list = file_metadata["Fwfilelinktolocal"].split("/")
    old_file_name_list[-1] = file_name # updated filename
    file_metadata["Fwfilelinktolocal"] = "/".join(old_file_name_list)
    file_path_to_save = os.path.abspath(folder + "/" + file_metadata["Fwfilelinktolocal"])
    file_metadata["Fwfilelinktolocal"] = file_path_to_save
    file_metadata["Fwfilename"] = file_path_to_save.split("\\")[-1]
    logger.debug('<%s> -> Downloading Firmware <%s>', url, file_path_to_save)
    with open(file_path_to_save, "wb") as fp_:
        fp_.write(resp.content)
    write_metadata_to_db([file_metadata])
    logger.info("File metadata added in DB")

def download_list_files(metadata, file_path, max_files=-1): #max_files -1 means download all files
    if max_files == -1:
        max_files = len(metadata)
    if max_files > len(metadata):
        max_files = len(metadata)
    for file_ in range(max_files):
        download_single_file(metadata[file_], file_path)

def write_metadata_to_db(metadata):
    logger.info("Going to write metadata in db")
    db_ = Database()
    for fw_ in metadata:
        if os.path.isfile(fw_["Fwfilelinktolocal"]):
            fw_["Checksum"] = get_hash_value(fw_["Fwfilelinktolocal"])
            meta_data = metadata_extractor(fw_["Fwfilelinktolocal"])
            fw_["Filesize"] = meta_data['File Size']
            fw_["Lasteditdate"] = meta_data['Last Edit Date']

            db_.insert_data(dbdictcarrier=fw_)
            logger.info('<Metadata added to database>')
            logger.debug('<%s> <ABB> <%s> <%s> <%s>', fw_['Fwfilename'], fw_['Modelname'], fw_['Version'], fw_['Releasedate'])

def se_get_total_firmware_count(url):
    req_body = {
        "Filters":[{"Criteria":0,"Origin":0,"Values":["Root"]},{"Criteria":1,"Origin":1,"Values":["Software"]}],
        "ResultsControl":{
            "PageNumber":1,
            "PageSize":1,
            "Sort":[{"SortBy":"Score","SortOrder":"Descending"}]
        },
        "Display":{"IncludeAllRevisions":False,"ResultsTranslationLanguage":"en"}
    }
    req = requests.post(url, json=req_body)
    json_resp = req.json()
    count = json_resp["numberOfAllHits"]
    logger.info("<Firmware Files Count>: %d", count)
    return count

def get_firmware_data_using_api(url, fw_count, fw_per_page):
    total_pages = math.ceil(fw_count/fw_per_page)
    fw_list = []
    for page in range(1, total_pages+1):
        req_body = {
            "Filters":[{"Criteria":0,"Origin":0,"Values":["Root"]},{"Criteria":1,"Origin":1,"Values":["Software"]}],
            "ResultsControl":{
                "PageNumber": page,
                "PageSize": fw_per_page,
                "Sort":[{"SortBy":"Score","SortOrder":"Descending"}]
            },
            "Display":{"IncludeAllRevisions":False,"ResultsTranslationLanguage":"en"}
        }
        response = requests.post(url, json=req_body)
        if response.status_code != 200:
            raise ValueError("Invalid API response with status_code = %d" % response.status_code)
        if page != total_pages:
            logger.info("Received metadata for %d/%d", page*fw_per_page, fw_count)
        else:
            logger.info("Received metadata for all %d/%d firmwares", fw_count, fw_count)
        fw_list += response.json()["documents"]
    return fw_list

def transform_metadata_format_ours(raw_data, local_storage_dir="."):
    fw_mod_list = []
    for fw_ in raw_data:
        # Check if firmware is in SKIP_FILES and skip it
        if fw_["metadata"].get("fileSuffix", None) and  fw_["metadata"]["fileSuffix"] in SKIP_FILES:
            continue
        local_link = os.path.join(local_storage_dir, str(uuid.uuid4()) + "." + fw_["metadata"]["fileSuffix"])

        fw_mod = {
            'Fwfileid': '',
            'Fwfilename': local_link.split("\\")[-1], #temp name
            'Manufacturer': 'abb',
            'Modelname': fw_["metadata"]["identification"]["documentNumber"],
            'Version': fw_["metadata"]["identification"]["revision"],
            'Type': fw_["metadata"]["documentKind"],
            'Releasedate': fw_["metadata"]["publishedDate"],
            'Filesize': '',
            'Lasteditdate': '',
            'Checksum': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': fw_["metadata"]["currentRevisionUrl"],
            'Fwfilelinktolocal': local_link, #setting temp filename as of now
            'Fwadddata': json.dumps({"summary": fw_["metadata"]["summary"].replace("'","")}),
            'Uploadedonembark': '',
            'Embarkfileid': '',
            'Startedanalysisonembark': ''
        }
        fw_mod_list.append(fw_mod)
    return fw_mod_list

def main():
    logger.info('<module ABB> -> Download Module started at <%s>', datetime.now())
    url = URL
    folder = DATA['file_paths']['download_files_path']
    if not os.path.isdir(folder):
        os.mkdir(folder)
    total_fw = se_get_total_firmware_count(url)
    raw_fw_list = get_firmware_data_using_api(url, total_fw, 1000)
    logger.info("Printing first Raw document metadata")
    logger.info(json.dumps(raw_fw_list[0], indent=4))
    metadata = transform_metadata_format_ours(raw_fw_list, local_storage_dir=os.path.abspath(folder))
    logger.info("Printing first transformed document metadata")
    logger.info(json.dumps(metadata[0], indent=4))
    download_list_files(metadata, file_path=folder, max_files=5)


if __name__ == "__main__":
    main()
