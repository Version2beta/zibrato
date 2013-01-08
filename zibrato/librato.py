from backend import Backend
from fuzzywuzzy import process
from time import time
import requests
import simplejson as json
import re
import collections
import argparse
import threading

API = 'https://metrics-api.librato.com/v1/metrics'

TYPES_OF_METRICS = [
      'counters', 'gauges'
    ]

Measurement = collections.namedtuple(
    'Measurement',
    'name, value, source, measure_time'
  )

class Librato(Backend):
  def connect(self):
    r = requests.head(API, auth = (self.username, self.apitoken))
    return r.status_code
  def parse(self, message):
    print message
    (level, mtype, name, value, timestamp, source) = message.split('|')
    if mtype == 'Timer': mtype = 'gauges'
    (mtype, confidence) = process.extractOne(
        mtype, TYPES_OF_METRICS)
    source = re.sub(r'[^A-Za-z0-9.:-_]', ':', source)
    return ( mtype,
             Measurement._make((name, float(value), source, timestamp)))
  def rollup_counters(self):
    if not self.queue.has_key('counters'):
      return
    counter = {}
    timestamp = str(int(float(time())))
    for item in self.queue['counters']:
      try:
        counter[item.source + '|' + item.name] += item.value
      except KeyError:
        counter[item.source + '|' + item.name] = item.value
    del self.queue['counters']
    for (k, v) in counter.iteritems():
      (source, name) = k.split('|')
      self.post(
          '|'.join(('', 'gauges', name, str(v), timestamp, source)))
  def flush(self):
    if self.queue:
      self.rollup_counters()
      auth = (self.username, self.apitoken)
      data = json.dumps(self.queue)
      headers = {'content-type': 'application/json'}
      r = requests.post(API, auth = auth, data = data, headers = headers)
      self.queue = {}
      if r.status_code > 200:
        raise IOError(r.text + ' ' + data)
      else: 
        return r.status_code

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description = 'Librato backend worker for Zibrato')
  parser.add_argument('--host',
      help = 'Zibrato backend FQDN or IP',
      default = '127.0.0.1')
  parser.add_argument('--port',
      help = 'Zibrato backend port',
      default = '5551')
  parser.add_argument('--username',
      help = 'Librato username')
  parser.add_argument('--apitoken',
      help = 'Librato API token')
  parser.add_argument('--levels',
      help = 'Subscribe to which levels')
  parser.add_argument('--flush',
      help = 'Flush time in seconds')
  args = parser.parse_args()
  l = Librato(
      host = args.host,
      port = args.port,
      username = args.username,
      apitoken = args.apitoken)
  for level in args.levels.split(','):
    l.subscribe(level.strip())
  count_measurements = 0
  count_flushes = 0
  start = int(time())
  while True:
    try:
      l.post(l.receive())
      if int(time()) >= start + int(args.flush):
        l.flush()
        count_flushes += 1
        start = int(time())
    except KeyboardInterrupt:
      raise KeyboardInterrupt('%d measurements / %d flushes' % 
          (count_measurements, count_flushes))
    count_measurements += 1

