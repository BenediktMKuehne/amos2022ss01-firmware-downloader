import inspect
import json
import os
import sys
import time
import platform
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from utils.chromium_downloader import ChromiumDownloader
from utils.database import Database
from utils.metadata_extractor import metadata_extractor
from utils.modules_check import vendor_field
from utils.Logs import get_logger
sys.path.append(os.path.abspath(os.path.join('.', '')))
logger = get_logger("vendors.openwrt")
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


class Openwrt:
    def __init__(self):
        # All the required data is initialized in this function
        with open(os.path.join(parent_dir, 'config', 'config.json'), 'rb') as json_file:
            json_data = json.loads(json_file.read())
            dummy_openwrt_data = json_data['openwrt']
            if vendor_field('openwrt', 'user'):
                self.email = vendor_field('openwrt', 'user')
            else:
                logger.error('<module : openwrt > -> user not present')
                raise Exception("< module :openwrt> user can't be found")
            if vendor_field('openwrt', 'password'):
                self.password = vendor_field('openwrt', 'password')
            else:
                logger.error('<module : openwrt > -> password not present')
                raise Exception("< module :openwrt> user can't be found")
            if vendor_field('openwrt', 'url'):
                self.url = vendor_field('openwrt', 'url')
            else:
                logger.error('<module : openwrt > -> url not present')
                self.url = "https://openwrt.org/"
                logger.info('<module : openwrt > -> using hardcode url')
            self.down_file_path = json_data['file_paths']['download_files_path']
        self.path = os.getcwd()
        self.system = platform.platform().lower()
        self.chrome_path = fr"{parent_dir}\utils\chromedriver.exe".replace('\\', '/') if 'win' in self.system else \
            fr"{parent_dir}\utils\chromedriver".replace('\\', '/')
        self.driver = webdriver.Chrome(service=Service(executable_path=self.chrome_path))
        self.dbdict = {
            'Fwfileid': '',
            'Fwfilename': '',
            'Manufacturer': '',
            'Modelname': '',
            'Version': '',
            'Type': '',
            'Releasedate': '',
            'Filesize': '',
            'Lasteditdate': '',
            'Checksum': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': '',
            'Fwfilelinktolocal': '',
            'Fwadddata': '',
            'Uploadedonembark': '',
            'Embarkfileid': '',
            'Startedanalysisonembark': ''
        }

    def homepage(self):
        # The homepage is used to navigate to the main page of downloads
        driver = self.driver
        driver.get(self.url)
        driver.implicitly_wait(10)
        driver.maximize_window()

    def write_database(self, filename, release_date, download_link, local_file_location, sha256sum):
        # The data extracted is writing into the database file
        dbdict_carrier = {}
        db_used = Database()
        metadata = metadata_extractor(str(local_file_location.replace("\\", "/")))
        for key in self.dbdict:
            if key == "Manufacturer":
                dbdict_carrier[key] = "OpenWRT"
            elif key == "Fwfilename":
                dbdict_carrier[key] = filename
            elif key == "Releasedate":
                dbdict_carrier[key] = release_date
            elif key == "Filesize":
                dbdict_carrier[key] = metadata["File Size"]
            elif key == "Lasteditdate":
                dbdict_carrier[key] = metadata["Last Edit Date"]
            elif key == "Fwdownlink":
                dbdict_carrier[key] = download_link
            elif key == "Fwfilelinktolocal":
                dbdict_carrier[key] = str(local_file_location.replace("\\", "/"))
            elif key == "Checksum":
                dbdict_carrier[key] = metadata["Hash Value"]
            elif key == "Fwadddata":
                dbdict_carrier[key] = "sha256sum = " + sha256sum
            else:
                dbdict_carrier[key] = ''
        db_used.insert_data(dbdict_carrier)
        logger.info('<Metadata added to database>')
        logger.debug('%s: Openwrt: %s', dbdict_carrier['Fwfilename'], dbdict_carrier['Releasedate'])

    def down_ele_click(self, release_date, download_link, sha256sum):
        # A fn for duplication Check for not to download the files if files exist in local machine
        filename = download_link.split('/')[-1].replace(" ", "_")
        path_to_download = r"{}\{}\OpenWRT\{}".format(self.path, self.down_file_path, self.driver.find_element(
            By.XPATH, "(//h1/a)[last()]").get_attribute("href")[30:].replace("/", "\\"))
        local_file_path = os.path.join(path_to_download.replace('\\', '/'), filename)
        if not os.path.isfile(local_file_path):
            if not os.path.exists(path_to_download):
                os.makedirs(path_to_download)
            req = requests.get(download_link, stream=True)
            if req.ok:
                with open(local_file_path, 'wb') as file:
                    for chunk in req.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            file.write(chunk)
                            file.flush()
                            os.fsync(file.fileno())
            self.write_database(filename, release_date, download_link, local_file_path, sha256sum)
            logger.debug("Openwrt: Downloading firmware %s", filename)
            logger.debug("%s: Downloading firmware %s", download_link, local_file_path)

    def crawl_table(self):
        # A fn used to navigate to the folders and sub folders of the download page and download them
        driver = self.driver
        files = driver.find_elements(By.XPATH, "//td[@class='n']/a[not(contains(text(),'packages'))]")
        for file in range(len(files)):
            driver.find_element(By.XPATH,
                                r"(//td[@class='n']/a[not(contains(text(),'packages'))])[{}]".format(file + 1)).click()
            try:
                if driver.find_element(By.XPATH, "//th[text()='Image for your Device']").is_displayed():
                    image_files = driver.find_elements(By.XPATH,
                                                       "//th[text()='Image for your Device']/ancestor::tbody//td/a")
                    for image_file in range(len(image_files)):
                        # file_name = driver.find_element(By.XPATH,"(//th[text()='Image for your Device']/ancestor::tbody//td/a)[{}]".format(image_file + 1))
                        sha256sum = driver.find_element(By.XPATH,
                                                        "(//th[text()='Image for your Device']/ancestor::tbody//td[@class='sh'])[{}]".format(
                                                            image_file + 1)).text
                        # file_size = driver.find_element(By.XPATH,
                        #                                 "(//th[text()='Image for your Device']/ancestor::tbody//td[@class='s'])[{}]".format(
                        #                                     image_file + 1)).text
                        release_date = driver.find_element(By.XPATH,
                                                           "(//th[text()='Image for your Device']/ancestor::tbody//td[@class='d'])[{}]".format(
                                                               image_file + 1)).text
                        download_link = driver.find_element(By.XPATH,
                                                            "(//th[text()='Image for your Device']/ancestor::tbody//td/a)[{}]".format(
                                                                image_file + 1)).get_attribute("href")
                        self.down_ele_click(release_date, download_link, sha256sum)
                        logger.debug("Downloading firmware from web page %s", driver.current_url)
            except NoSuchElementException:
                self.crawl_table()
            driver.back()
            time.sleep(1)

    def stable_release(self):
        # A fn used to navigate to the downloads page
        driver = self.driver
        driver.find_element(By.XPATH, '//button[text()="OK"]').click()
        driver.find_element(By.LINK_TEXT, 'Downloads').click()
        driver.find_element(By.LINK_TEXT, 'Stable Release builds').click()
        self.crawl_table()

    def close_browser(self):
        # At the end of the program, the function will close the Chrome browser
        driver = self.driver
        time.sleep(10)
        driver.quit()


if __name__ == '__main__':
    ChromiumDownloader().executor()
    ow = Openwrt()
    try:
        ow.homepage()
        ow.stable_release()
    except NoSuchElementException as error:
        print(error)
    finally:
        ow.close_browser()
