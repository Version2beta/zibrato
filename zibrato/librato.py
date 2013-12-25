from time import time
import re
from collections import namedtuple
import argparse
import simplejson as json
import requests
from fuzzywuzzy import process
from .backend import Backend

__version_info__ = (0, 1, 8)
__version__ = ".".join([str(x) for x in __version_info__])

USER_AGENT = 'zibrato/%s' % __version__
API = 'https://metrics-api.librato.com/v1/metrics'
TYPES_OF_METRICS = ['counters', 'gauges']

Measurement = namedtuple('Measurement',
                         ('name', 'value', 'source', 'measure_time'))


class Librato(Backend):

    def connect(self):
        r = requests.head(
            API,
            auth=(self.username, self.apitoken),
            headers = {'User-Agent': USER_AGENT})
        return r.status_code

    def parse(self, message):
        print message
        level, mtype, name, value, timestamp, source = message.split('|')
        if mtype == 'Timer':
            mtype = 'gauges'
        mtype, confidence = process.extractOne(mtype, TYPES_OF_METRICS)
        source = re.sub(r'[^A-Za-z0-9.:-_]', ':', source)
        return mtype, Measurement(name, float(value), source, timestamp)

    def rollup_counters(self):
        if not 'counters' in self.queue:
            return
        counter = {}
        timestamp = str(int(time()))
        for item in self.queue['counters']:
            name = item.source + '|' + item.name
            counter[name] = counter.get(name, 0) + item.value
        del self.queue['counters']
        for k, v in counter.iteritems():
            source, name = k.split('|')
            self.post('|'.join(('', 'gauges', name, str(v),
                                timestamp, source)))

    def flush(self):
        if not self.queue:
            return
        self.rollup_counters()
        auth = (self.username, self.apitoken)
        data = json.dumps(self.queue)
        headers = {
            'content-type': 'application/json',
            'User-Agent': USER_AGENT,
        }
        r = requests.post(
            API,
            auth=auth,
            data=data,
            headers=headers)
        self.queue = {}
        if r.status_code > 200:
            raise IOError(r.text + ' ' + data)
        return r.status_code


def main():
    parser = argparse.ArgumentParser(
        description='Librato backend worker for Zibrato',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', default='127.0.0.1',
                        help='Zibrato backend FQDN or IP')
    parser.add_argument('--port', type=int, default=5551,
                        help='Zibrato backend port')
    parser.add_argument('--username',
                        help='Librato username')
    parser.add_argument('--apitoken',
                        help='Librato API token')
    parser.add_argument('--levels',
                        help='Subscribe to which levels')
    parser.add_argument('--flush', type=float,
                        help='Flush time in (float) seconds')
    args = parser.parse_args()
    l = Librato(
        host=args.host,
        port=args.port,
        username=args.username,
        apitoken=args.apitoken)
    for level in args.levels.split(','):
        l.subscribe(level.strip())
    count_measurements = 0
    count_flushes = 0
    start = time()
    while True:
        try:
            l.post(l.receive())
            if time() >= start + args.flush:
                l.flush()
                count_flushes += 1
                start = time()
        except KeyboardInterrupt:
            raise KeyboardInterrupt('%d measurements / %d flushes' %
                                    (count_measurements, count_flushes))
        count_measurements += 1

if __name__ == "__main__":
    main()
