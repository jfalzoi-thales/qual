The following directory contains a package that we build and add
to the Thales mps-builder package repo for the Qual build:

    lookbusy

The following directories contain snapshots of RPMs built by the
Thales mps-builder when building the Qual image, and are provided
here for the convenience of developers setting up a development
machine:

    pmbw
    protobuf
    zmq

The following additional packages are required by Qual software,
but the mps-builder Qual build pulls standard CentOS packages for
them, so they can just be installed using 'yum':

    fio
    iperf3
    pyserial
    python-lxml
    python-netifaces
