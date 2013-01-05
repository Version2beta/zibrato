from backend import Backend
from fuzzywuzzy import process
import requests
import simplejson as json
import re

API = 'https://metrics-api.librato.com/v1/metrics'

class Librato(Backend):
  def connect(self):
    r = requests.head(API, auth = (self.username, self.apitoken))
    return r.status_code
  def parse(self, message):
    ( level, mtype, name, value,
      timestamp, source ) = super(Librato, self).parse(message)
    if mtype == 'timer': mtype = 'gauges'
    source = re.sub(r'[^A-Za-z0-9.:-_]', ':', source)
    return { mtype:
             { name:
               { "value": value,
                 "measure_time": timestamp,
                 "source": source
               }
             }
           }
  def post(self, message):
    auth = (self.username, self.apitoken)
    data = json.dumps(self.parse(message))
    headers = {'content-type': 'application/json'}
    r = requests.post(API, auth = auth, data = data, headers = headers)
    if r.status_code > 200:
      return str(r.status_code), r.text
    else:
      return r.status_code
