import sys
import os
sys.path.append("..") 
sys.path.append(os.path.join(sys.path[0], '..'))

from time import sleep

import zmq
from threading import Thread
from zibrato import Zibrato
from expecter import expect

def publisher():
  """Publish stuff to test we can receive it."""
  context = zmq.Context.instance()
  socket = context.socket(zmq.PUB)
  socket.bind('ipc:///tmp/testing')
  while True:
    try:
      socket.send('test|test_if_we_queued_a_message')
    except zmq.ZMQError as e:
      if e.errno == zmq.ETERM:
        break
      else:
        raise
    sleep(0.001)

globalContext = zmq.Context.instance()
p_thread = Thread(target=publisher)
p_thread.start()

class TestThatZibratoIsAvailable:
  """
  Start with making sure the class is present and acts right for the
  developer.
  """
  def test_starting_zibrato_with_a_default_socket(self):
    z = Zibrato()
    expect(z.connected()) == True
  def test_starting_zibrato_with_a_specified_socket(self):
    z = Zibrato('ipc:///tmp/mySocket')
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
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('ipc:///tmp/testing')
    socket.setsockopt(zmq.SUBSCRIBE, 'test')
    received = socket.recv()
    expect(received) == 'test|test_if_we_queued_a_message'
    globalContext.term()



