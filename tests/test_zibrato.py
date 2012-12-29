import sys
import os
sys.path.append("..") 
sys.path.append(os.path.join(sys.path[0], '..'))

from zibrato import Zibrato
from expecter import expect

class TestThatZibratoIsAvailable:
  def test_starting_zibrato_with_a_default_socket(self):
    z = Zibrato()
  def test_starting_zibrato_with_a_specified_socket(self):
    z = Zibrato('mySocket')
    

class TestSendingAMessageToZeroMQ:
  def test_if_we_can_queue_a_message(self):
    pass

