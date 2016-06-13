This file contains the packages needed to support ZeroMQ (ZMQ)
communication on CentOS Linux.  There are 3 files, two RPMs containing
the necessary system libraries, and a Python egg for Python 2.7.

The RPMs were downloaded from the CentOS repository, and the Python egg
was built from the pyzmq 15.2.0 package from PyPI.

To install:

  sudo rpm -Uv openpgm-5.2.122-2.el7.x86_64.rpm zeromq3-3.2.5-1.el7.x86_64.rpm
  sudo easy_install pyzmq-15.2.0-py2.7-linux-x86_64.egg

