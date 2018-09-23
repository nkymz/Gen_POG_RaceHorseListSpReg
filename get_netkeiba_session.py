# -*- coding: utf-8 -*-

import os
import time

import openpyxl
import requests

PATH = os.getenv("HOMEDRIVE", "None") + os.getenv("HOMEPATH", "None") + "/Dropbox/POG/"
WBPATH = (PATH + "POG_HorseList.xlsx").replace("\\", "/")
LOGIN_URL = "https://regist.netkeiba.com/account/"


def get_netkeiba_session():
    wb = openpyxl.load_workbook(WBPATH)
    ws_settings = wb["Settings"]
    login_id = ws_settings["B2"].value
    password = ws_settings["B3"].value
    wb.close()
    login_info = {
        'pid': 'login',
        'action': 'auth',
        'return_url2': '',
        'mem_tp': '',
        'login_id': login_id,
        'pswd': password,
        'auto_login': ''
    }

    mysession = requests.Session()
    time.sleep(1)
    mysession.post(LOGIN_URL, data=login_info)

    return mysession
