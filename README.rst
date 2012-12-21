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

@count_me('counter_name')
    Increment a counter named 'counter_name' each time the decorated function
    is called.

Count_me('counter_name', interval = 1)
    Increment a counter named 'counter_name'. To increment by an interval other
    than one, set interval to the amount.

@time_me('timer_name')
    Record the decorated function's execution time under a gauge named
    'timer_name'.

Time_me('timer_name')
    Record the time spent within a given context.
  
    Example::

        import zibrato
        ...
        with Time_me('timer_name'):
          pass

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

