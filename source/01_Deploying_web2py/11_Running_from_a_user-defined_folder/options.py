# -*- coding: utf-8 -*-


import socket
import os

ip = '0.0.0.0'
port = 80
interfaces=[('0.0.0.0',80),
            ('0.0.0.0',443,'ssl_key.pem','ssl_certificate.pem')]
password = '<recycle>'  # <recycle> means use the previous password
pid_filename = 'httpserver.pid'
log_filename = 'httpserver.log'
profiler_filename = None
#ssl_certificate = 'ssl_cert.pem'  # certificate file
#ssl_private_key = 'ssl_key.pem'  # private key file
#numthreads = 50 # ## deprecated; remove
minthreads = None
maxthreads = None
server_name = socket.gethostname()
request_queue_size = 5
timeout = 30
shutdown_timeout = 5
folder = "/path/to/apps" # <<<<<<<< edit this line
extcron = None
nocron = None

