import zmq
from time import sleep, time
from datetime import datetime
from functools import wraps
from contextlib import contextmanager

class Zibrato:
  """
  Zibrato class sets up the connection to ZeroMQ and provides the timer and
  counter methods used to make measurements.
  """
  def __init__(self, **kwargs):
    context = kwargs.get('context') or zmq.Context()
    host = kwargs.get('host') or '127.0.0.1'
    port = kwargs.get('port') or 5550
    self.context = context
    self.socket = self.context.socket(zmq.PUB)
    self.socket.connect('tcp://%s:%d' % (host, int(port)))
    self.socket.setsockopt(zmq.LINGER, 0)

  def close(self):
    self.socket.close()

  def connected(self):
    return not self.socket.closed

  def pack(self, **kwargs):
    level = kwargs.get('level') or 'info'
    mtype = kwargs.get('mtype') or 'Gauge'
    name = kwargs.get('name') or 'default'
    value = str(kwargs.get('value') or 1)
    source = kwargs.get('source') or "not_specified"
    timestamp = str(int(float(time())))
    message = '%s|%s|%s|%s|%s|%s' % ( level, mtype, name, value,
                                      timestamp, source )
    return message

  def send(self, **kwargs):
    self.socket.send(self.pack(**kwargs))

  def gauge(self, **kwargs):
    self.send(**kwargs)

  def time_me(self, **decargs):
    def inner(f):
      def wrapper(*args, **kwargs):
        start = datetime.now()
        ret = f(*args, **kwargs)
        total = datetime.now() - start
        decargs['mtype'] = decargs.get('mtype') or 'Timer'
        decargs['name'] = decargs.get('name') or 'default_timer'
        decargs['value'] = str(total.seconds + total.microseconds/1000000.00)
        self.send(**decargs)
        return ret
      return wraps(f)(wrapper)
    return inner

  @contextmanager
  def Time_me(self, **kwargs):
    start = datetime.now()
    yield
    total = datetime.now() - start
    kwargs['mtype'] = kwargs.get('mtype') or 'Timer'
    kwargs['name'] = kwargs.get('name') or 'default_timer'
    kwargs['value'] = str(total.seconds + total.microseconds/1000000.00)
    self.send(**kwargs)

  def count_me(self, **decargs):
    def inner(f):
      def wrapper(*args, **kwargs):
        ret = f(*args, **kwargs)
        decargs['mtype'] = decargs.get('mtype') or 'Counter'
        decargs['name'] = decargs.get('name') or 'default_counter'
        decargs['value'] = str(decargs.get('value') or 1)
        self.send(**decargs)
        return ret
      return wraps(f)(wrapper)
    return inner

  @contextmanager
  def Count_me(self, **kwargs):
    yield
    kwargs['mtype'] = kwargs.get('mtype') or 'Counter'
    kwargs['name'] = kwargs.get('name') or 'default_counter'
    kwargs['value'] = str(kwargs.get('value') or 1)
    self.send(**kwargs)


