import zmq
from fuzzywuzzy import process

class Backend(object):
  def __init__(self, **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)
    if not vars().has_key('socket'):
      socket = 'ipc:///tmp/zibrato'
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect(socket)
  def subscribe(self, sub):
    self.socket.setsockopt(zmq.SUBSCRIBE, sub)
  def receive_one(self):
    self.socket.RCVTIMEO = 100
    ret = self.socket.recv()
    self.socket.RCVTIMEO = 0
    return ret
  def parse(self, message):
    (level, mtype, name, value, timestamp, source) = message.split('|')
    mtypes = ['counters', 'timer', 'gauges']
    (mtype, confidence) = process.extractOne(mtype, mtypes)
    return (level, mtype, name, value, timestamp, source)
  def connect(self):
    pass
  def post(self):
    pass

