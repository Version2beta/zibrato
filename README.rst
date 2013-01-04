Zibrato
==========

Zibrato provides a decorator that records metrics for a function. The metrics 
go first to a local ZeroMQ and then to Librato. Other backends such as statsd
are contemplated for the future.

Usage
-----

Zibrato consists of two parts. First, it provides the zibrato module used for
instrumenting code.

Zibrato module
______________

z = Zibrato(socket)
    Set up a metrics handler. Socket can be any transport and endpoint
    supported by 0MQ's bind function. See http://api.zeromq.org/2-1:zmq-bind.

@z.count_me(name = 'counter_name')
    Increment a counter named 'counter_name' each time the decorated function
    is called.

z.Count_me(name = 'counter_name', value = 4)
    Increment a counter named 'counter_name'. To increment by an interval other
    than one, set value to the amount.

@z.time_me(name = 'timer_name')
    Record the decorated function's execution time under a gauge named
    'timer_name'.

z.Time_me(name = 'timer_name')
    Record the time spent within a given context.
  
z.gauge(name = 'gauge_name', value=123)
    Record a value.

Metric decorators and context managers take up to four arguments:

    * level: Monitoring level, modeled after logging levels (i.e. debug,
      info, warning, error, critical). Zibrato workers can be configured to
      pay attention to only specified levels.
    * mtype: Type of metric, typically 'counter', 'timer', and 'gauge'.
    * name: Name of the metric being recorded.
    * value: Value to record. For timing functions, this is overwritten by the
      time. For counters, value represents the quantity by which the counter
      should be incremented. For gauges, this is the fixed reading.

Example code::

    import zibrato
    z = Zibrato('ipc:///tmp/mysocket')
    ...
    @z.time_me(name = 'myfunct_timer')
    def myfunctt():
      time_consuming_operations()
    ...
    @z.count_me(name = "myfunct_counter')
    def myfunctc():
      pass
    ...
    with z.Count_me(level = 'info', name = 'counter_name'):
      pass
    ...
    with z.Time_me(level = 'debug', name = 'timer_name'):
      slow_function_to_time()

Zibrato workers
_______________

Zibrato also includes a worker that processes queued messages and sends them to Librato.

Example::

    python /usr/local/lib/python2.7/dist-packages/zibrato/workers/librato.py --username USERNAME --apikey KEY

Alternatively, the worker can be run from supervisord::

    [program:zibrato_librato]
    command=python /usr/local/lib/python2.7/dist-packages/zibrato/workers/librato.py --username USERNAME --apikey KEY
    process_name=%(program_name)s
    autostart=true
    autorestart=true
    stopsignal=QUIT
    user=www-data

Options::

    zibrato 
    --username  Librato username
    --apikey    Librato API key
    --hostname  Librato hostname, defaults to "metrics-api.librato.com"
    --apipath   Librato path, defaults to "/v1/"

