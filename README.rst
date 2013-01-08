Zibrato
==========

Zibrato provides Python decorators and context managers that instrument code.
It attempts to do this very efficiently, so the metrics are collected and
then shifted into a ZeroMQ queue, where a backend process can collect them
and send them to Librato. Other backends such as statsd are contemplated for
the future.

Installation
------------

Zibrato is available through PyPi at http://pypi.python.org/pypi/Zibrato/.

Alternatively, one should be able to clone this repository and run pip install
with the requirements.txt file.

Please note that pyzmq is an installation prerequisite. Ubuntu users (and
probably others) will need the python-dev package installed in order to build
pyzmq::

    sudo apt-get install python-dev

Usage
-----

Zibrato consists of two parts. First, it provides the zibrato module used for
instrumenting code.

Zibrato module
______________

from zibrato import Zibrato
    Librato, Backend, and Broker modules also available. See code.

z = Zibrato()
    Set up a new instance of Zibrato to use in your code. Accepts several
    settings:

    * host: The FQDN or IP address with which to connect. Optional.
      Defaults to '127.0.0.1'. See "Zibrato workers" below.
    * port: The port with which to connect. Optional. Defaults to 5550.
    * context: A ZeroMQ context instance. This is completely optional and
      only desirable under advanced circumstances where ZeroMQ is being
      used in other ways, too.

@z.count_me(level = 'info', name = 'counter_name')
    Increment a counter named 'counter_name' each time the decorated function
    is called.

z.Count_me(level = 'info', name = 'counter_name', value = 4)
    Increment a counter named 'counter_name'. To increment by an interval other
    than one, set value to the amount.

@z.time_me(level = 'debug', name = 'timer_name')
    Record the decorated function's execution time under a gauge named
    'timer_name'.

z.Time_me(level = 'debug', name = 'timer_name')
    Record the time spent within a given context.
  
z.gauge(level = 'crit', name = 'gauge_name', value=123)
    Record a value.

Zibrato decorators, of course, return the result of the wrapped function.
Context managers return None as they are not intended to be used from within
the 'with' block. The gauge method returns None also.

Metric decorators and context managers take up to four arguments:

* level: Required. Monitoring level, modeled after logging levels (i.e.
  debug, info, warning, error, critical) but completely arbitrary so you
  can use whatever labels work for you. Zibrato workers are configured to
  pay attention to only specified levels.
* mtype: Required. Type of metric, typically 'counter', 'timer', and
  'gauge'. See "Metric types" below.
* name: Required. Name of the metric being recorded.
* value: Value to record. For timing functions, value is neither required
  nor desirable to provide, and if provided it will be replaced by the
  measured time. For counters, value represents the quantity by which the
  counter should be incremented, and defaults to 1 if not provided. For
  gauges, this is the fixed reading and should be provided.
* source: The source of the metric. This might represent the name of the
  program, class, or server for instance. Optional and defaults to
  'not_specified'.

Example code::

    import zibrato
    z = Zibrato()
    # or z = Zibrato(host = '127.0.0.1', port = '5550')
    ...
    @z.time_me(level = 'debug', name = 'myfunct_timer', source = 'myprog')
    def myfunctt():
      time_consuming_operations()
    ...
    @z.count_me(level = 'info', name = "myfunct_counter', value = 5) # inc by 5
    def myfunctc():
      pass
    ...
    with z.Count_me(level = 'info', name = 'counter_name', source = 'deathstar'):
      pass
    ...
    with z.Time_me(level = 'debug', name = 'timer_name'):
      slow_function_to_time()
    ...
    z.gauge(level = 'crit', name = 'gauge_name', value=123)

Zibrato workers
_______________

Zibrato requires a backend worker (actually a 'broker') that connects one or
more publishers of measurements (source code being run in parallel) to one or
more measurement backends (Librato and Statsd, for example.)

The Zibrato broker
++++++++++++++++++

The Zibrato broker runs as a daemon under supervisord or other process
controller. It provides a TCP endpoint for the Zibrato publishers (code
instruments) to send measurements, and a TCP endpoint to which the Zibrato
backends can subscribe to get measurements for sending off to other services.

The broker might be started like this::

    python /usr/local/lib/python2.7/dist-packages/zibrato/backend.py \
        --host 127.0.0.1 --port 5550

where 'host' specifies the IP address or FQDN and 'port' specifies the lower
port of a consecutive pair to which the broker should bind. Both host and port
are optional. Default values are 127.0.0.1 and 5550, respectively. The lower
port address is used to listen to Zibrato publishers (see 'Zibrato module'
above) and the higher port is used to publish to Zibrato workers (see 'Zibrato
workers' below).

The preferred way to start the Zibrato backend would be to use a service such
as supervisord::

    [program:zibrato_backend]
    command=python /usr/local/lib/python2.7/dist-packages/zibrato/backend.py \
        --host 127.0.0.1 --port 5550
    process_name=%(program_name)s
    autostart=true
    autorestart=true
    stopsignal=QUIT
    user=www-data

Zibrato workers
+++++++++++++++

This version of Zibrato also includes a worker that processes queued
measurements and sends them to Librato.

Example::

    python /usr/local/lib/python2.7/dist-packages/zibrato/librato.py \
        --username USERNAME --apitoken KEY --levels test,debug,info --flush 60

The available parameters are:

* --host: The FQDN hostname or IP address of the Zibrato backend.
* --port: The port to which the Zibrato work should connect. This is the
  higher of the two ports in the pair, and one greater than the port
  specified when starting the backend.
* --levels: The levels to which this worker should subscribe.
* --flush: The frequency with which the measurements should be sent to
  Librato.
* --username: The Librato username for connecting to their API.
* --apitoken: The Librato API Token for connecting to their API.

Alternatively, the worker can be run from supervisord::

    [program:zibrato_librato]
    command=python /usr/local/lib/python2.7/dist-packages/zibrato/librato.py \
        --username USERNAME --apitoken KEY --levels info,warn --flush 60
    process_name=%(program_name)s
    autostart=true
    autorestart=true
    stopsignal=QUIT
    user=www-data

Creating a new Zibrato worker
+++++++++++++++++++++++++++++

New Zibrato backend workers should subclass the Backend class specified in 
zibrato/backend.py. They probably need to reimplement the connect, parse,
post, and flush methods, and must include code for running as __main__. See
zibrato/librato.py as an example.

Metric types
____________

* Counters. Zibrato counters keep track of how many times an event with
  a common name happens between two flushes on the back end. So for
  example, let's say you're keeping track of how may times 'myfunct' is
  called, and you're flushing your data to the back end every 60 seconds.
  If you don't specify a value, then the 'myfunct_counter' will be
  incremented by one each time the counter is encountered, sent to Librato
  and reset to zero every 60 seconds. If source is specified, the counter
  uniquely tracked by source and name, rather than just name. The
  timestamp for a counter is given as the time the counter is flushed.
* Gauges. Gauges hold a value at a given time. Each gauge measurement
  is recorded to the backend with a timestamp for the time Zibrato
  received the measurement.
* Timers. Zibrato provides a special gauge that it fills in automatically
  with the amount of time something took. Time is measured in seconds to
  microsecond resolution using Python's datetime.now() method.

Please note that the Zibrato backend is ultimately responsible for
implementing how each metric type is recorded. In this release only one
backend is provided, but in future releases check with the backend
documentation to determing exactly how a metric behaves.

Please also note that Zibrato was originally written to provide code
instrumentation specifically and to connect to Librato specifically. This
introduces an impedence mismatch, as Librato's availble metric types as of
this writing are limited to gauges and counters, and Librato's counters
don't work the way we need our counters to work. So the metrics implemented
in this code translate into only gauges at Librato.

Other business
--------------

Tests
_____

Zibrato includes nose tests in the tests/ directory.

Pull requests
_____________

Pull requests are welcome!

Thank you
_________

Special thanks to Tracy Harms @kaleidic who coached me on Agile methodologies
and test driven development, plus helped tease out the intricasies of ZeroMQ
and the architecture of this program.

Also, thank you to regulars on #zeromq who answered beginner questions
patiently.

License
_______

Zibrato is released under a 3-clause BSD license, which can be read in the
LICENSE.txt file.
