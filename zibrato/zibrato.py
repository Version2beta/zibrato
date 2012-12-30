import zmq
from timer import Timer
from counter import Counter

class Zibrato:
  """
  Zibrato class sets up the connection to ZeroMQ and provides the timer and
  counter methods used to make measurements.
  """
  def __init__(self, socket = 'ipc:///tmp/zibrato'):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind(socket)
    self.counter = Counter(self)

  def connected(self):
    return not self.socket.closed

  def send(self, *args):
    self.socket.send('|'.join(args))
    return 

