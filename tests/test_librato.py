import sys
import os
sys.path.append('..') 
sys.path.append(os.path.join(sys.path[0], '..'))

import zmq
import threading
import random
from zibrato import Zibrato, Librato, Backend
from expecter import expect
from time import sleep, time
from datetime import datetime

try:
  import config
except ImportError:
  raise ImportError(
        """

        Edit tests/config.py.dist and save as config.py to
        complete these tests.

        """
      )

b = Backend(socket = 'tcp://127.0.0.1:55551')
b.subscribe('testing_backend')
l = Librato(socket = 'tcp://127.0.0.1:55551',
            username = config.librato['username'],
            apitoken = config.librato['apitoken'])
l.subscribe('testing_librato')
z = Zibrato('tcp://127.0.0.1:55551')

class TestTheBackend:
  def test_that_we_can_retrieve_messages_from_the_queue(self):
    z.gauge(level = 'testing_backend',
            source = 'TestTheBackend',
            name = 'test_that_we_can_retrieve_messages_from_the_queue',
            value = 1)
    expect(b.receive_one()[0:73]) == (
          'testing_backend|Gauge|' +
          'test_that_we_can_retrieve_messages_from_the_queue|1')
  def test_that_we_can_parse_a_message(self):
    message = z.pack( level = 'testing_backend',
                      mtype = 'Counter',
                      source = 'TestTheBackend',
                      name = 'test_counter',
                      value = 5)
    mtype, parsed = b.parse(message)
    expect(parsed.name) == 'test_counter'
    expect(parsed.source) == 'TestTheBackend'
    expect(parsed.value) == 5
  def test_that_we_can_post_a_message(self):
    message = z.pack( level = 'testing_backend',
                      mtype = 'Counter',
                      source = 'TestTheBackend',
                      name = 'test_counter',
                      value = 5)
    b.post(message)
    resp = b.queue['counters'][0]._asdict()
    del resp['measure_time']
    expect(resp) == {
        'name': 'test_counter', 'value': 5.0, 'source': 'TestTheBackend'}

class TestLibrato:
  def test_that_we_can_parse_a_message(self):
    message = z.pack( level = 'testing_librato',
                      mtype = 'Counter',
                      source = 'TestLibrato',
                      name = 'test_counter',
                      value = 5)
    mtype, parsed = l.parse(message)
    expect(parsed.name) == 'test_counter'
    expect(parsed.source) == 'TestLibrato'
    expect(parsed.value) == 5
  def test_that_we_can_connect_to_librato(self):
    expect(l.connect()) == 200
  def test_that_we_can_send_a_gauge(self):
    message = z.pack( level = 'testing_librato',
                      mtype = 'Gauge',
                      source = 'TestLibrato',
                      name = 'test_that_we_can_send_a_gauge',
                      value = random.randrange(999))
    l.post(message)
    resp = l.flush()
    expect(resp) == 200
  def test_that_we_can_send_a_counter_from_zibrato(self):
    with z.Count_me(level = 'testing_librato', source = 'TestLibrato',
          name = 'test_that_we_can_send_a_counter_from_zibrato',
          value = datetime.now().second):
      pass
    l.post(l.receive_one())
    resp = l.flush()
    expect(resp) == 200
  def test_that_we_can_send_a_timer_from_zibrato(self):
    with z.Time_me(
          level = 'testing_librato',
          source = 'TestLibrato',
          name = 'test_that_we_can_send_a_timer_from_zibrato'
        ):
      sleep(0.01)
    l.post(l.receive_one())
    resp = l.flush()
    expect(resp) == 200
  def test_that_we_can_send_multiple_metrics(self):
    for x in range(2):
      message = z.pack( level = 'testing_librato',
                      mtype = 'Gauge',
                      source = 'TestLibrato' + str(x),
                      name = 'test_that_we_can_send_multiple_metrics.gauge',
                      value = random.randrange(100))
      l.post(message)
    for x in range(random.randrange(10)):
      message = z.pack( level = 'testing_librato',
                      mtype = 'Counter',
                      source = 'TestLibrato',
                      name = 'test_that_we_can_send_multiple_metrics.counter',
                      value = 1)
      l.post(message)
    resp = l.flush()
    expect(resp) == 200
  def test_that_we_can_roll_up_counters(self):
    for x in range(2):
      message = z.pack( level = 'testing_librato',
                      mtype = 'Counter',
                      source = 'TestLibrato' + str(x),
                      name = 'test_that_we_can_send_roll_up_counters',
                      value = 1)
      l.post(message)
    l.rollup_counters()
    expect(l.queue.has_key('counters')) == False
