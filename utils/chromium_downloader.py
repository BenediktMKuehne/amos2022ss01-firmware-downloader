import os
import platform
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
        self.system = platform.platform().lower()

    def load_and_extract(self):
        """ The fn is used to trigger the api to get the latest version, then it allows to trigger
        download, unzip and delete the zip file"""
        response = requests.get(self.latest_release_url, allow_redirects=True).text
        sys_carrier = {
            'linux': 'chromedriver_linux64.zip',
            'mac': 'chromedriver_mac64.zip',
            'mac_m1': 'chromedriver_mac64_m1.zip',
            'win': 'chromedriver_win32.zip'
        }
        print(f"System running on {self.system}")
        system = [item for item in sys_carrier if item in self.system.lower()][0]
        download_url = "https://chromedriver.storage.googleapis.com/{}/{}".format(response, sys_carrier[system])
        print(parent_dir)
        print(response, download_url)
        chromium_zip = wget.download(download_url, fr'{parent_dir}\utils\chromedriver.zip'.replace('\\', '/'))
        print(fr'{parent_dir}\utils\chromedriver.zip'.replace('\\', '/') if os.path.isfile(fr'{parent_dir}\utils\
                                                                        chromedriver.zip'.replace('\\', '/'))else None)
        with zipfile.ZipFile(chromium_zip, 'r') as zip_ref:
            zip_ref.extractall(fr'{parent_dir}\utils'.replace('\\', '/'))
        if os.path.isfile(fr'{parent_dir}\utils\chromedriver.exe'.replace('\\', '/')) and 'win' in self.system:
            print(fr'file found and is at {parent_dir}\utils\chromedriver.exe'.replace('\\', '/'))

        if os.path.isfile(fr'{parent_dir}\utils\chromedriver'.replace('\\', '/')) and 'win' not in self.system:
            print(fr'file found and is at {parent_dir}\utils\chromedriver'.replace('\\', '/'))
            os.chmod(fr'{parent_dir}\utils\chromedriver'.replace('\\', '/'), 777)

        os.remove(chromium_zip)

    def executor(self):
        # Checksum for chromedriver
        #if os.path.exists(fr'{parent_dir}\utils\chromedriver.exe'.replace('\\', '/')) and 'win' in self.system:
        #    os.remove(fr'{parent_dir}\utils\chromedriver.exe'.replace('\\', '/'))

        # if os.path.exists(fr'{parent_dir}\utils\chromedriver'.replace('\\', '/')) and 'win' not in self.system:
        #    os.remove(fr'{parent_dir}\utils\chromedriver'.replace('\\', '/'))

        # if "chromedriver.exe" not in os.listdir(fr'{parent_dir}\utils'.replace('\\', '/')) and 'win' in self.system:
        #    print("chromedriver.exe is not present in local path, so installing chromedriver.exe")
        #    self.load_and_extract()

        if "chromedriver" not in os.listdir(fr'{parent_dir}\utils'.replace('\\', '/')) and 'win' not in self.system:
            print("chromedriver is not present in local path, so installing chromedriver")
            self.load_and_extract()
