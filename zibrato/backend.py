import zmq
from collections import namedtuple
import argparse
from fuzzywuzzy import process

__version_info__ = (0, 1, 8)
__version__ = ".".join([str(x) for x in __version_info__])

TYPES_OF_METRICS = ['counters', 'timers', 'gauges']

Measurement = namedtuple('Measurement',
                         ('name', 'value', 'source', 'measure_time'))


class Backend(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # ugly preservation of `default if kwarg is None else kwarg` semantic
        self.host = getattr(self, 'host', None) or '127.0.0.1'
        self.port = getattr(self, 'port', None) or 5551
        self.context = getattr(self, 'context', None) or zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://%s:%d' % (self.host, int(self.port)))
        self.queue = {}

    def subscribe(self, sub):
        self.socket.setsockopt(zmq.SUBSCRIBE, sub)

    def receive_one(self):
        self.socket.RCVTIMEO = 100
        ret = self.socket.recv()
        self.socket.RCVTIMEO = 0
        return ret

    def receive(self):
        return self.socket.recv()

    def parse(self, message):
        level, mtype, name, value, timestamp, source = message.split('|')
        mtype, confidence = process.extractOne(mtype, TYPES_OF_METRICS)
        return mtype, Measurement(name, float(value), source, timestamp)

    def connect(self):
        pass

    def post(self, message):
        mtype, measurement = self.parse(message)
        if mtype not in self.queue:
            self.queue[mtype] = []
        self.queue[mtype].append(measurement)

    def flush(self, message):
        self.queue = {}

    def close(self):
        self.socket.close()


class Broker(object):

    def __init__(self, **kwargs):
        self.host = kwargs.get('host') or '127.0.0.1'
        self.port = int(kwargs.get('port')) or 5550
        self.context = kwargs.get('context') or zmq.Context.instance()
        self.frontend = self.context.socket(zmq.SUB)
        self.frontend.bind('tcp://%s:%d' % (self.host, self.port))
        self.frontend.setsockopt(zmq.SUBSCRIBE, '')
        self.backend = self.context.socket(zmq.PUB)
        self.backend.bind('tcp://%s:%d' % (self.host, self.port + 1))
        self.backend.setsockopt(zmq.LINGER, 0)

    def main(self):
        try:
            zmq.device(zmq.FORWARDER, self.frontend, self.backend)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.frontend.close()
                self.backend.close()
            else:
                raise


def main():
    parser = argparse.ArgumentParser(
        description='Backend manager for Zibrato',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', default='127.0.0.1',
                        help='TCP address first or FQDN of listener')
    parser.add_argument('--port', type=int, default=5550,
                        help='Lower port of pair')
    args = parser.parse_args()
    b = Broker(host=args.host, port=args.port)
    b.main()


if __name__ == "__main__":
    main()
