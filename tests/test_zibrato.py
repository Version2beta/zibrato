import sys
import os
sys.path.append('..') 
sys.path.append(os.path.join(sys.path[0], '..'))

import zmq
import threading
from zibrato import Zibrato
from expecter import expect
from time import sleep

SOCKET = 'ipc:///tmp/testing'

class Receiver:
  """
  Create a ZeroMQ subscriber. This is what will "hear" Zibrato publish
  messages. Must be done before initializing Zibrato.
  """
  def __init__(self, socket = SOCKET):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect(socket)
  def receive(self, sub = 'testing'):
    self.socket.setsockopt(zmq.SUBSCRIBE, sub)
    received = self.socket.recv()
    return received

receiver = Receiver(SOCKET)
z = Zibrato(SOCKET)

class TestThatZibratoIsAvailable:
  """
  Start with making sure the class is present and acts right for the
  developer.
  """
  def test_starting_zibrato_with_a_specified_socket(self):
    expect(z.connected()) == True
  def test_starting_zibrato_with_an_invalid__socket(self):
    with expect.raises(zmq.ZMQError):
      z = Zibrato('oops:///tmp/mySocket')
  def test_starting_zibrato_with_a_default_socket(self):
    z = Zibrato()
    expect(z.connected()) == True

class TestSendingAMessageToZeroMQ:
  def test_if_we_queued_a_message(self):
    z_thread = threading.Thread(target=z.send, args=('testing', 'test_if_we_queued_a_message'))
    z_thread.start()
    expect(receiver.receive()) == 'testing|test_if_we_queued_a_message'

class TestMetricsInGeneral:
  def test_that_metrics_send_to_queue_with_default_values(self):
    z_thread = threading.Thread(target=z.metric, kwargs={})
    z_thread.start()
    expect(receiver.receive('info')) == 'info'
    pass

