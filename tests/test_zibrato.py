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
  def receive(self, sub):
    if sub:
      self.socket.setsockopt(zmq.SUBSCRIBE, sub)
    self.socket.RCVTIMEO = 1000
    try:
      received = self.socket.recv()
    except zmq.ZMQError as e:
      return e.strerror
    except:
      raise
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
    z_thread = threading.Thread(target = z.send, kwargs = ({'level': 'testing', 'value': 'test_if_we_queued_a_message'}))
    z_thread.start()
    expect(receiver.receive('testing')[0:49]) == 'testing|Gauge|default|test_if_we_queued_a_message'
  def test_that_we_can_fail_to_receive_a_message_with_report(self):
    z_thread = threading.Thread(target = z.send, kwargs = ({'level': 'failme', 'value': 'test_if_we_queued_a_message'}))
    z_thread.start()
    expect(receiver.receive('testing')) == 'Resource temporarily unavailable'

class TestMetricsAsDecorators:
  @z.count_me(level = 'info', name = 'countertest')
  def function_that_will_be_counted(self):
    pass
  def test_counter_as_decorator(self):
    self.function_that_will_be_counted()
    received = receiver.receive('info') 
    count = float(received.split('|')[3])
    expect(count) == 1
  @z.count_me(level = 'info', name = 'countertest', value = 5)
  def function_that_will_be_counted_plus_five(self):
    pass
  def test_counter_as_decorator_with_larger_increment(self):
    self.function_that_will_be_counted_plus_five()
    received = receiver.receive('info') 
    count = float(received.split('|')[3])
    expect(count) == 5
  @z.time_me(level = 'info', name = 'timertest')
  def function_that_takes_some_time(self):
    sleep(0.1)
  def test_timer_as_decorator(self):
    self.function_that_takes_some_time()
    received = receiver.receive('info')
    time = float(received.split('|')[3])
    expect(time) >= 0.100

class TestMetricsAsContextManagers:
  def test_counter_as_a_context_manager(self):
    with z.Count_me(level = 'info', name = 'countermanager'):
      pass
    received = receiver.receive('info') 
    count = float(received.split('|')[3])
    expect(count) == 1
  def test_counter_plus_five_as_a_context_manager(self):
    with z.Count_me(level = 'info', name = 'countermanager', value = 5):
      pass
    received = receiver.receive('info') 
    count = float(received.split('|')[3])
    expect(count) == 5
  def test_timer_as_a_context_manager(self):
    with z.Time_me(level = 'info', name='timermanager'):
      sleep(0.1)
    received = receiver.receive('info')
    time = float(received.split('|')[3])
    expect(time) >= 0.100

class TestGauges:
  def test_gauge_with_value(self):
    z.gauge(level = 'testing', name = 'test_gauge', value = 999)
    received = receiver.receive('testing')
    expect(received[0:28]) == 'testing|Gauge|test_gauge|999'
