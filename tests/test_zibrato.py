import sys
import os
sys.path.append('..') 
sys.path.append(os.path.join(sys.path[0], '..'))

from time import sleep

import zmq
import threading
from zibrato import Zibrato
from expecter import expect

SOCKET = 'ipc:///tmp/testing'

class TestThatZibratoIsAvailable:
  """
  Start with making sure the class is present and acts right for the
  developer.
  """
  def test_starting_zibrato_with_a_default_socket(self):
    z = Zibrato()
    expect(z.connected()) == True
  def test_starting_zibrato_with_a_specified_socket(self):
    z = Zibrato(SOCKET)
    expect(z.connected()) == True
  def test_starting_zibrato_with_an_invalid__socket(self):
    with expect.raises(zmq.ZMQError):
      z = Zibrato('oops:///tmp/mySocket')

class TestSendingAMessageToZeroMQ:
  global globalContext
  def test_if_we_can_send_a_message(self):
    z = Zibrato()
    expect(z.send('test', 'This is a test')) == None
  def test_if_we_queued_a_message(self):
    publisher = Publisher(SOCKET, 'testing|test_if_we_queued_a_message')
    publisher.start()
    receiver = Receiver()
    expect(receiver.receive()) == 'testing|test_if_we_queued_a_message'

class TestCountingThings:
  def test_counters_as_decorators(self):
    pass

class Receiver:
  """Create a ZeroMQ subscriber."""
  def __init__(self, socket = SOCKET):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect(socket)
  def __del__(self):
    del self.socket
    self.context.term()
  def receive(self, sub = 'testing'):
    self.socket.setsockopt(zmq.SUBSCRIBE, sub)
    received = self.socket.recv()
    return received

class Publisher(threading.Thread):
  """Create a Zibrato message."""
  def __init__(self, socket = SOCKET, msg = 'testing|'):
    threading.Thread.__init__(self)
    self.z = Zibrato(socket)
    self.msg = msg
  def run(self):
    sleep(0.05)
    self.z.send(self.msg)
    sleep(0.05)

