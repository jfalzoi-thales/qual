#!/bin/bash

# Generate a config file for libvirt
/thales/host/appliances/genvmconfig /opt/thales/mps/livecd-mps-guest-*.vm.qcow2 > /tmp/qual_guest.xml

# Start the VM
virsh create /tmp/qual_guest.xml
