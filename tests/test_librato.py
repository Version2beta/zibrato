import sys
import os
sys.path.append('..') 
sys.path.append(os.path.join(sys.path[0], '..'))

import zmq
import threading
from zibrato import Zibrato, Librato
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

l = Librato(username = config.librato['username'],
            apitoken = config.librato['apitoken'])
l.subscribe('testing')
z = Zibrato()

class TestTheQueue:
  def test_that_we_can_retrieve_messages_from_the_queue(self):
    z.gauge(level = 'testing',
            source = 'TestTheQueue',
            name = 'test_that_we_can_retrieve_messages_from_the_queue',
            value = 1)
    expect(l.receive_one()[0:65]) == (
          'testing|Gauge|' +
          'test_that_we_can_retrieve_messages_from_the_queue|1'
        )
  def test_that_we_can_parse_a_message(self):
    message = z.pack( level = 'testing',
                      mtype = 'Counter',
                      source = 'TestTheQueue',
                      name = 'test_counter',
                      value = 5)
    parsed = l.parse(message)
    del parsed['counters']['test_counter']['measure_time']
    result = { 'counters':
               { 'test_counter':
                 { 'value': '5',
                   'source': 'TestTheQueue'
                 }
               }
             }
    expect(parsed) == result

class TestLibrato:
  def test_that_we_can_connect_to_librato(self):
    expect(l.connect()) == 200
  def test_that_we_can_send_a_metric(self):
    message = z.pack( level = 'testing',
                      mtype = 'Counter',
                      source = 'TestLibrato',
                      name = 'test_that_we_can_send_a_metric',
                      value = 999)
    resp = l.post(message)
    expect(resp) == 200
  def test_that_we_can_send_a_counter_from_zibrato(self):
    with z.Count_me(
          level = 'testing',
          source = 'TestLibrato',
          name = 'test_that_we_can_send_a_counter_from_zibrato',
          value = datetime.now().second
        ):
      pass
    resp = l.post(l.receive_one())
    expect(resp) == 200
  def test_that_we_can_send_a_timer_from_zibrato(self):
    with z.Time_me(
          level = 'testing',
          source = 'TestLibrato',
          name = 'test_that_we_can_send_a_timer_from_zibrato'
        ):
      sleep(0.01)
    resp = l.post(l.receive_one())
    expect(resp) == 200
