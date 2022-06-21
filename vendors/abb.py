import json
import os
import math
import uuid

import requests
import os
from urllib.parse import urlparse
import sys
sys.path.append(os.path.abspath(os.path.join('.', '')))  
from utils.database import Database


def download_single_file(file_metadata):
    url = file_metadata["Fwdownlink"]
    print(f"Donwloading {url} ")
    resp = requests.get(url, allow_redirects=True)
    if resp.status_code != 200:
        raise ValueError("Invalid Url or file not found")
    final_obj_url = resp.request.url
    file_name = urlparse(final_obj_url).path.split("/")[-1].replace("%20", " ")
    old_file_name_list = file_metadata["Fwfilelinktolocal"].split("/")
    old_file_name_list[-1] = file_name # updated filename
    file_metadata["Fwfilelinktolocal"] = "/".join(old_file_name_list)
    file_path_to_save = file_metadata["Fwfilelinktolocal"]
    print(f"File saved at {file_path_to_save}")
    with open(file_path_to_save, "wb") as f:
        f.write(resp.content)
    write_metadata_to_db([file_metadata])
    print("File metadata added in DB")

def download_list_files(metadata, max_files=-1): #max_files -1 means download all files
    if max_files == -1:
        max_files = len(metadata)
    if max_files > len(metadata):
        max_files = len(metadata)
    for file_ in range(max_files):
        download_single_file(metadata[file_])

def write_metadata_to_db(metadata):
    print("Going to write metadata in db")
    db_name = 'firmwaredatabase.db'
    db = Database(dbname=db_name)
    if db_name not in os.listdir('../'):
        db.create_table()
    for fw in metadata:
        db.insert_data(dbdictcarrier=fw)

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
    r = requests.post(url, json=req_body)
    json_resp = r.json()
    count = json_resp["numberOfAllHits"]
    print(f"Found total {count} Firmware files")
    return count
    
def get_firmware_data_using_api(url, fw_count, fw_per_page):
    if fw_count < fw_per_page:
        fw_pr_page = fw_count
    total_pages = math.ceil(fw_count/fw_per_page)
    fw_list = list()
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
            raise ValueError(f"Invalid API response with status_code = {response.status_code}")
        if page != total_pages:
            print(f"Received metadata for {page*fw_per_page}/{fw_count}")
        else:
            print(f"Received metadata for all {fw_count}/{fw_count} firmwares")
        fw_list += response.json()["documents"]
    return fw_list

def transform_metadata_format_ours(raw_data, local_storage_dir="."):
    fw_mod_list = list()
    for fw in raw_data:
        fw_mod = {
	    'Fwfileid': str(uuid.uuid4()),
	    'Manufacturer': 'abb',
	    'Modelname': fw["metadata"]["identification"]["documentNumber"],
	    'Version': fw["metadata"]["identification"]["revision"],
	    'Type': fw["metadata"]["documentKind"],
	    'Releasedate': fw["metadata"]["publishedDate"],
	    'Checksum': '',
	    'Embatested': '',
	    'Embalinktoreport': '',
	    'Embarklinktoreport': '',
            'Fwdownlink': fw["metadata"]["currentRevisionUrl"],
            'Fwfilelinktolocal': os.path.join(local_storage_dir, str(uuid.uuid4()) + "." + fw["metadata"]["fileSuffix"]), #setting temp filename as of now
            'Fwadddata': json.dumps({"summary": fw["metadata"]["summary"].replace("'","")})
	}
        fw_mod_list.append(fw_mod)
    return fw_mod_list

if __name__ == "__main__":
    url = "https://discoveryapi.library.abb.com/api/public/documents"
    folder = 'File_system'
    if not os.path.isdir(folder):
        os.mkdir(folder)
    total_fw = se_get_total_firmware_count(url)
    raw_fw_list = get_firmware_data_using_api(url, total_fw, 1000)
    print("Printing first Raw document metadata")
    print(json.dumps(raw_fw_list[0], indent=4))
    metadata = transform_metadata_format_ours(raw_fw_list, local_storage_dir=os.path.abspath(folder))
    print("Printing first transformed document metadata")
    print(json.dumps(metadata[0], indent=4))
    download_list_files(metadata)
