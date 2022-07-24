import os
import zipfile
import sys
import inspect
import requests
import wget
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.abspath(os.path.join('.', '')))


class ChromiumDownloader:
    # The ChromiumDownloader is responsible to check and download if no Chromium Downloader is present at local repo

    def __init__(self):
        self.url = 'https://chromedriver.storage.googleapis.com'
        self.latest_release_url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'

    def load_and_extract(self):
        """ The fn is used to trigger the api to get the latest version, then it allows to trigger
        download, unzip and delete the zip file"""
        response = requests.get(self.latest_release_url, allow_redirects=True).text
        download_url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(response)
        print(parent_dir)
        print(response, download_url)
        chromium_zip = wget.download(download_url, fr'{parent_dir}\utils\chromedriver.zip')
        with zipfile.ZipFile(chromium_zip, 'r') as zip_ref:
            zip_ref.extractall()
        os.remove(chromium_zip)

    def executor(self):
        # Checksum for chromedriver
        if os.path.exists(fr'{parent_dir}\utils\chromedriver.exe'):
            os.remove(fr'{parent_dir}\utils\chromedriver.exe')
        if "chromedriver.exe" not in os.listdir(fr'{parent_dir}\utils'):
            print("chromedriver.exe is not present in local path, so installing chromedriver")
            self.load_and_extract()
