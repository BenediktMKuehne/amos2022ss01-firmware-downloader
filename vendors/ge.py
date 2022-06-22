import requests
from bs4 import BeautifulSoup
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
sys.path.append(os.path.abspath(os.path.join('.', '')))  
from utils.database import Database
from utils.check_duplicates import check_duplicates
from utils.Logs import get_logger
import requests
from webdriver_manager.chrome import ChromeDriverManager
import time
import json


name = "ge"
logger = get_logger("vendors.ge")
directories_link = ["/communications/mds/software.asp?directory=Orbit_MCR", "/communications/mds/software.asp?directory=Master_Station", "/communications/mds/software.asp?directory=TD-Series", "/communications/mds/software.asp?directory=TD-Series/Support+Items", "/communications/mds/software.asp?directory=SD_Series", "/communications/mds/software.asp?directory=TransNET/Previous", "/communications/mds/software.asp?directory=SD_Series", "/communications/mds/software.asp?directory=entraNET"]


user = ''
passw = ''

with open('config/config.json', 'r') as f:
    data = json.load(f)
    user = data['ge']['user']
    passw = data['ge']['password']

#inserting meta data into database
def insert_into_db(data, db_name):
    db = Database(dbname=db_name)
    if db_name not in os.listdir('.'):
        db.create_table()
    db.insert_data(dbdictcarrier=data)
    logger.info("data inserted")

#download firmware image
def download_file(url, file_path_to_save, data0, data1, folder, filename, link, main_url, click, db_name, is_file_download):
    
    local_uri = "./" + folder + "/" + filename
    req_data = {
		'Fwfileid': 'FILE',
        'Fwfilename': data0,
		'Manufacturer': 'GE',
		'Modelname': os.path.splitext(data0)[0],
		'Version': '',
		'Type': '',
		'Releasedate': data1,
		'Checksum': 'None',
		'Embatested': '',
		'Embalinktoreport': '',
		'Embarklinktoreport': '',
		'Fwdownlink': url,
		'Fwfilelinktolocal': local_uri,
		'Fwadddata': ''
	}

    if(check_duplicates(req_data, db_name) == False or is_file_download == True):
        if(link != "javascript:;"):
            logger.info(f"Downloading {url} and saving as {file_path_to_save}")
            resp = requests.get(url, allow_redirects=True)
            if resp.status_code != 200:
                raise ValueError("Invalid Url or file not found")
            with open(file_path_to_save, "wb") as f:
                f.write(resp.content)
            if(is_file_download == False):
                insert_into_db(req_data, db_name)
        else:
            options = webdriver.ChromeOptions()
            prefs = {"download.default_directory" : file_path_to_save}
            options.add_argument("headless")
            options.add_experimental_option("prefs",prefs)
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
            # Go to your page url
            try:
                URL = "https://www.gegridsolutions.com/Passport/Login.aspx"
                driver.get(URL)
                driver.find_element(By.ID, "ctl00_BodyContent_Login1_UserName").send_keys(user)
                driver.find_element(By.ID, "ctl00_BodyContent_Login1_Password").send_keys(passw)
                driver.find_element(By.ID, "ctl00_BodyContent_Login1_LoginButton").click()
                # Get button you are going to click by its id ( also you could us find_element_by_css_selector to get element by css selector)
                driver.get(main_url)
                driver.execute_script(click)
                time.sleep(60)
                driver.close()
                if(is_file_download == False):
                    insert_into_db(req_data, db_name)
            except:
                logger.error("Error in downloading")

    else:
        logger.info("Data already exist!")

#parse html and start clean according to our need
def scraper_parse(url, folder, base_url):
    dest = os.path.join(os.getcwd(), folder)
    try:
        if not os.path.isdir(dest):
            os.mkdir(dest)
    except Exception as e:
        raise ValueError(f"{e}")
    cont = requests.get(url)
    soup = BeautifulSoup(cont.text, 'html.parser')
    items = soup.find_all("tr", valign="top")
    data = []
    click = ""
    for item in items:
        sub_data = []
        items_temp = item.find_all("td")
        if(len(items_temp)):
            if(items_temp[0].get_text().find(".zip") != -1 or items_temp[0].get_text().find(".mpk") != -1 or items_temp[0].get_text().find(".S28") != -1):
                for item_temp in items_temp:
                    if(items_temp.index(item_temp) == 0):
                        link = item_temp.findChild("a").get("href")
                        if(link == "javascript:;"):
                            click = item_temp.findChild("a").get("onclick")
                        file_path = os.path.join(dest, item_temp.get_text())
                        download_file(base_url + link, file_path, items_temp[0].get_text(), items_temp[1].get_text(), folder, item_temp.get_text(), link, url, click, 'firmwaredatabase.db', False)
                    sub_data.append(item_temp.get_text())
                data.append(sub_data)

def main():
    data = {}
    with open('config/test_config.json', 'r') as f:
        data = json.load(f)
    paths = directories_link
    base_url = data['ge']['url']

    folder = 'File_system'

    for path in paths:
        url = base_url + path
        scraper_parse(url, folder, base_url)

if __name__ == "__main__":
    main()
