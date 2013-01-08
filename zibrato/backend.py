import zmq
import collections
import argparse
from fuzzywuzzy import process
from time import sleep

TYPES_OF_METRICS = [
      'counters', 'timers', 'gauges'
    ]

Measurement = collections.namedtuple(
    'Measurement',
    'name, value, source, measure_time'
  )

class Backend(object):
  def __init__(self, **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)
    context = kwargs.get('context') or zmq.Context()
    host = kwargs.get('host') or '127.0.0.1'
    port = kwargs.get('port') or 5551
    self.context = context
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect('tcp://%s:%d' % (host, int(port)))
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
    (level, mtype, name, value, timestamp, source) = message.split('|')
    (mtype, confidence) = process.extractOne(
        mtype, TYPES_OF_METRICS)
    return ( mtype,
             Measurement._make((name, float(value), source, timestamp)))
  def connect(self):
    pass
  def post(self, message):
    mtype, measurement = self.parse(message)
    try:
      self.queue[mtype].append(measurement)
    except KeyError:
      self.queue[mtype] = [measurement]
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
    self.backend.bind('tcp://%s:%d' % (self.host, self.port+1))
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

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description = 'Backend manager for Zibrato')
  parser.add_argument('--host', default = '127.0.0.1',
      help='TCP address first or FQDN of listener (default 127.0.0.1)')
  parser.add_argument('--port', default = '5550',
      help='Lower port of pair (default 5550)')
  args = parser.parse_args()
  b = Broker(host = args.host, port = args.port)
  b.main()

