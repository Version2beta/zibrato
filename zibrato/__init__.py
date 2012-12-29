import zmq

__all__ = [
      'Counter',
      'Timer',
    ]

class Zibrato:
  def __init__(self, socket = 'zibrato'):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind('ipc:///tmp/' + socket)

