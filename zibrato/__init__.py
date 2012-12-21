#!/usr/bin/env python
# coding=utf-8
# zibrato
"""

  zibrato
  ~~~~~~~

  Zibrato provides a decorator that records metrics for a function
  first to ZeroMQ and then via a worker thread, to Librato. 

"""

from zibrato import *
import zmq
from functools import wraps
from datetime import datetime

__all__ = [ 'time_me',
            'count_me',
            'Time_me',
            'Count_me',
          ]

