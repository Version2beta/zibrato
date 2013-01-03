import zmq
from time import sleep
from metric import *

class Zibrato:
  """
  Zibrato class sets up the connection to ZeroMQ and provides the timer and
  counter methods used to make measurements.
  """
  def __init__(self, socket = 'ipc:///tmp/zibrato'):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind(socket)
    self.metric = Metric(self)
    #self.counter = Counter(self)
    #self.timer = Timer(self)
    #self.gauge = Gauge(self)
    sleep(0.05)

  def connected(self):
    return not self.socket.closed

  def send(self, *args):
    self.socket.send('|'.join(args))
    return 

