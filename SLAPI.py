#!/usr/bin/env python
import logging
import requests
import requests_cache
import pprint
import sys
import json
import codecs
import os
from datetime import timedelta
from copy import deepcopy

session=requests.Session()

class SLAPI:
    def __init__(self, apiKey="1234", host="http://api.sl.se", apiversion="2"):
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.apiversion = apiversion
        #self.user = user
        self.apiKey = apiKey
        # FIXME handle ValidTo
        self.SessionKey = ""
        self.ValidTo = ""
        self.ErrorMessage = ""
        self.normalizeMap = {
            'CardID': unicode('CardId'),
            'CardPrimarySerialNumber': unicode('PrimarySerialNumber'),
            'CardFirstName': unicode('FirstName'),
            'CurrentStatus': unicode('CardStatus'),
            'CardStatus': unicode('CurrentStatus'),
        }

        self.s = requests.Session()

        #self._login()
        #requests_cache.install_cache('seriline_api')
        # make sure cache directory exists
        try:
            os.makedirs("cache")
        except OSError:
            if not os.path.isdir("cache"):
                raise


    def _http_request(self, resource, payload=None, method="GET"):
       """ Perform an HTTP GET/POST request against the given endpoint. """
       # Avoid dangerous default function argument `{}`
       payload = payload or {}
       # versioning an API guarantees compatibility
       endpoint = '{}/{}'.format(self.host, resource)
       try:
           if method == "GET":
               res = self.s.get(
                   endpoint,
                   # attach parameters to the url, like `&foo=bar`
                   params=payload,
                   # tell the API we expect to parse JSON responses
                   #headers={'Accept': 'text/json;'}
               )
           elif method == "POST":
               res = self.s.post(
                   endpoint,
                   # attach parameters to the url, like `&foo=bar`
                   data=payload,
               )
           res.raise_for_status()
           if res.ok:
               return res.json()
               #if "ResponseData" in res:
                   #return res._content.json()
               #else:
                   #return res.json()
       except requests.exceptions.RequestException as e:
           print e
           sys.exit(1)

    def _get_nocache(self, resource, payload={}):
        return self._request(resource, payload)
        with requests_cache.disabled():
            return self._request(resource, payload)

    def _request(self, resource, payload={}, method="GET"):
        # TODO Check SessionKey and ValidTo
        payload["SessionKey"] = self.SessionKey
        data = self._http_request(resource, payload, method=method)
        # FIXME verify data is dict
        if "StatusCode" in data:
            if data["StatusCode"]==0:
                return data
            else:
                print "Get Error: {}".format(data.get("ErrorMessage"))
                self.ErrorMessage = data.get("ErrorMessage")
                #pprint.pprint(data)
                #pprint.pprint(vars(data))
                return None
        elif "Message" in data:
                print "Got Error: {}".format(data.get("Message"))
        else:
            print "Error: No Response From API"
            self.ErrorMessage = data.get("ErrorMessage")
            #pprint.pprint(data)
            return None


    def _login(self):
        data = self._http_request("api/Authentication/Login", { "username": self.user, "apiKey": self.apiKey })
        if "Success" in data:
            if data["Success"] is True:
                self.SessionKey = data.get("SessionKey")
                self.ValidTo = data.get("ValidTo")
            else:
                print "Login Error: %s" % data.get("Error Message")
                return None
        else:
            print "Error: No Response From API"
            return None

        return True

    def _normalize(self, d):
        ret = {}
        for (key, value) in d.items():
            if key == "DataFields":
                ret.update(dict(zip([x['Tag'] for x in value], [x['Value'].replace("\t","") for x in value])))
                continue

            if key in self.normalizeMap:
                key = self.normalizeMap.get(key)

            ret[key] = value

        return ret
    def GetDeviations(self,DeviationData):
        DeviationData['key']=self.apiKey
        res = self._request("api%s/deviations.json" % self.apiversion,DeviationData,method="GET")
        return res
#http://api.sl.se/api2/deviations.json?key=<DIN API KEY> & transportation mode = <TRANSPORT MODE> and line number = <LINE NUMBER> & SiteID = <SiteID> & from date = <FROM DATE> & todate = <todate>
