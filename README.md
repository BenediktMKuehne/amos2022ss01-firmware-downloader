# _Firmware Downloader (AMOS SS 2022)_

![image](https://user-images.githubusercontent.com/104498119/168901090-445c6709-dfa1-4592-a9bc-ab61af57d433.png)


## Project Title: 

Firmware Downloader and Management Tool

## Industry Partner: 
Siemens Energy

## Project Summary:

The software shall be able to
  download firmware images from vendor websites,
  extract metadata, and
  catalog them.

In a management console,
  users can trigger a download,
  review the results, and
  supply additional information.

## Further requirements: 

Downloads
  can be triggered repeatedly,
  are incremental, and
  can be accessed in the management dashboard for editing.

The software will only be applied to websites that do not object to automated downloading.

**Note**: Please go through the Project Description folder for detailed overview about the Project

## Requirements:

  Kali Linux
  Embark (https://github.com/e-m-b-a/embark)
  Pycharm (Recommended)

## Installation

Use the installer.sh to install project.

``` First of all follow the steps to install and run embark (https://github.com/e-m-b-a/embark) in your kali linux. ```

Then Run Following Command in the root folder of embark project:

```bash
sudo bash ./installer.sh
```

## Run

``` First of all register a user on Embark with username: test and password: test. You can also change username and password in config/config.json fileif you want. ```

Then Run Following Command in the root folder of project:

```bash
python main.py
```

current problem:
[devport](https://stackoverflow.com/questions/50642308/webdriverexception-unknown-error-devtoolsactiveport-file-doesnt-exist-while-t)