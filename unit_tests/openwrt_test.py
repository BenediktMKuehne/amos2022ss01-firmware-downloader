import inspect
import json
import os
import sys
import time
import unittest
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from utils.database import Database

sys.path.append(os.path.abspath(os.path.join('.', '')))
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


class WebCode(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(parent_dir, 'config', 'config.json'), 'rb') as json_file:
            json_data = json.loads(json_file.read())
            openwrt_data = json_data['openwrt']
            self.url = openwrt_data['url']
            self.down_file_path = json_data['file_paths']['download_files_path']
        self.driver = webdriver.Chrome()
        self.path = os.getcwd()
        self.dbdict = {
            'Fwfileid': '',
            'Fwfilename': '',
            'Manufacturer': '',
            'Modelname': '',
            'Version': '',
            'Type': '',
            'Releasedate': '',
            'Checksum': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': '',
            'Fwfilelinktolocal': '',
            'Fwadddata': ''
        }

    def test_homepage(self):
        driver = self.driver
        driver.get(self.url)
        driver.implicitly_wait(10)  # seconds
        driver.maximize_window()
        self.assertEqual("[OpenWrt Wiki] Welcome to the OpenWrt Project", driver.title, msg="Homepage testcase passed")

    def write_database(self, file_name, release_date, download_link, local_file_location, sha256sum):
        dbdict_carrier = {}
        db_used = Database()
        for key in self.dbdict:
            if key == "Manufacturer":
                dbdict_carrier[key] = "OpenWRT"
            if key == "Fwfilename":
                dbdict_carrier[key] = file_name
            if key == "Releasedate":
                dbdict_carrier[key] = release_date
            if key == "Fwdownlink":
                dbdict_carrier[key] = download_link
            if key == "Fwfilelinktolocal":
                dbdict_carrier[key] = str(local_file_location.replace("\\", "/"))
            if key == "Checksum":
                dbdict_carrier[key] = sha256sum
            if key not in dbdict_carrier:
                dbdict_carrier[key] = ''
            db_used.insert_data(dbdict_carrier)
            self.assertTrue(dbdict_carrier, msg="data inserted")

    def down_ele_click(self, release_date, download_link, sha256sum):
        # A fn for duplication Check for not to download the files if files exist in local machine
        filename = download_link.split('/')[-1].replace(" ", "_")
        path_to_download = r"{}\{}\OpenWRT\{}".format(self.path, self.down_file_path, self.driver.find_element(By.XPATH,
                                                                                                               "(//h1/a)[last()]").get_attribute(
            "href")[30:].replace("/", "\\"))
        local_file_path = os.path.join(path_to_download, filename)
        if not os.path.isfile(local_file_path):
            self.write_database(filename, release_date, download_link, local_file_path, sha256sum)
            print(f"The file is not found in local repository, now {filename} will be downloaded into local")
            if not os.path.exists(path_to_download):
                os.makedirs(path_to_download)
            r = requests.get(download_link, stream=True)
            if r.ok:
                with open(local_file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())
        else:
            print(f"The file is found in local repository, now {filename} will not be downloaded into local")
        return local_file_path

    def crawl_table(self):
        driver = self.driver
        files = driver.find_elements(By.XPATH, "//td[@class='n']/a[not(contains(text(),'packages'))]")
        for i in range(len(files)):
            driver.find_element(By.XPATH,
                                r"(//td[@class='n']/a[not(contains(text(),'packages'))])[{}]".format(i + 1)).click()
            try:
                if driver.find_element(By.XPATH, "//th[text()='Image for your Device']").is_displayed():
                    image_files = driver.find_elements(By.XPATH,
                                                       "//th[text()='Image for your Device']/ancestor::tbody//td/a")
                    for j in range(len(image_files)):
                        file_name = driver.find_element(By.XPATH,
                                                        "(//th[text()='Image for your Device']/ancestor::tbody//td/a)[{}]".format(
                                                            j + 1))
                        sha256sum = driver.find_element(By.XPATH,
                                                        "(//th[text()='Image for your Device']/ancestor::tbody//td[@class='sh'])[{}]".format(
                                                            j + 1)).text
                        # file_size = driver.find_element(By.XPATH,"(//th[text()='Image for your Device']/ancestor::tbody//td[@class='s'])[{}]".format(j + 1)).text
                        release_date = driver.find_element(By.XPATH,
                                                           "(//th[text()='Image for your Device']/ancestor::tbody//td[@class='d'])[{}]".format(
                                                               j + 1)).text
                        download_link = driver.find_element(By.XPATH,
                                                            "(//th[text()='Image for your Device']/ancestor::tbody//td/a)[{}]".format(
                                                                j + 1)).get_attribute("href")
                        local_file_path = self.down_ele_click(release_date, download_link, sha256sum)
                        self.assertTrue(local_file_path, msg="Location exists")
                        self.assertTrue(file_name, msg="download element found")
            except NoSuchElementException:
                self.crawl_table()
            driver.back()
            time.sleep(1)
            return "Passed"

    def test_stable_release(self):
        driver = self.driver
        driver.get(self.url)
        driver.implicitly_wait(10)  # seconds
        driver.maximize_window()
        driver.find_element(By.XPATH, '//button[text()="OK"]').click()
        driver.find_element(By.LINK_TEXT, 'Downloads').click()
        self.assertEqual("[OpenWrt Wiki] Downloads", driver.title, msg="Download page testcase passed")
        driver.find_element(By.LINK_TEXT, 'Stable Release builds').click()
        self.assertEqual("Index of /releases/", driver.title,
                         msg="Stable Release builds testcase passed")
        self.assertEqual(self.crawl_table(),"Passed")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
