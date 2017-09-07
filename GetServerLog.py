#coding=utf-8
"""
-------------------------------------------------------------------------------
Name:        getsvrlog.py
Purpose:     Collect ArcGIS Server Site Logs
Author:      Sean.L (luwl@esrichina.com.cn)
Created:     8/25/16
Copyright:   (c) Sean.L 2016
-------------------------------------------------------------------------------
"""

from __future__ import print_function

# 3rd-party library: requests
# http://docs.python-requests.org/en/latest/
# pip install requests
import requests
import json
import pandas as pd

SITE_LIST = ["http://192.168.1.75:6080/arcgis",""]
USER = "siteadmin"
PASSWORD = "esri"
LOGPATH = r"D:\\"

# note that services are suffixed by type when passed to admin REST API
SERVICES = [r"MajorCity.MapServer"]

class AGSRestError(Exception): pass
class ServerError(Exception): pass

def _validate_response(response):
    """ Tests response for HTTP 200 code, tests that response is json,
        and searches for typical AGS error indicators in json.
        Raises an exception if response does not validate successfully.
    """
    if not response.ok:
        raise ServerError("Server Error: {}".format(response.text))

    try:
        response_json = response.json()
        if "error" in response_json:
            raise AGSRestError(response_json["error"])
        if "status" in response_json and response_json["status"] != "success":
            error = response_json["status"]
            if "messages" in response_json:
                for message in response_json["messages"]:
                    error += "\n" + message
            raise AGSRestError(error)

    except ValueError:
        print(response.text)
        raise ServerError("Server returned HTML: {}".format(response.text))


def _get_token(site,username, password):
    """ Returns token from server """
    token_url = "{host}/tokens/".format(
        host=site)

    data = { "f": "json",
             "username": username,
             "password": password,
             "client": "requestip",
             "expiration": 5 }
    response = requests.post(token_url, data,verify=False)
    _validate_response(response)
    token = response.json()['token']
    return token

def _get_log(site):
    getlog_url="{host}/admin/logs/query?f=json".format(
        host=site)
    data = { "token": token,
             "startTime":'',
             "endTime":'',
             "level":'SEVERE',
             "filterType":'json',
             "filter":'{\"server\": \"*\",\
                        \"services\": \"*\",\
                        \"machines":\"*\" }',
             "pageSize":10000}
    response = requests.post(getlog_url, data,verify=False)
    _validate_response(response)
    response_json = response.json()
    #print (response_json['logMessages'])
    myFrame=pd.DataFrame(response_json['logMessages'])
    sitewaip= site[site.index("/")+2:site.index(":",7)]
    myFrame["sitewaip"]=sitewaip
    file_name = sitewaip.replace(".","_");
    myFrame.to_csv(r"{root}{site_name}.csv".format(root=LOGPATH,site_name=file_name), index=False)
    return myFrame


if __name__ == "__main__":
    frames = []
    for site in SITE_LIST:
        print("Retrieving token...")
        token = _get_token(site,USER, PASSWORD)
        print("Retrieved: {}".format(token))
        df = _get_log(site)
        print( df.columns)
        frames.append(df)
    all_frame = pd.concat(frames)
    all_frame.to_csv(r"{root}allsites.csv".format(root=LOGPATH),index=False)

