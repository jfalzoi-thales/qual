#!/bin/bash

# Start virtual network
virsh net-create /etc/libvirt/qemu/networks/default.xml

# Generate a config file for libvirt
/thales/host/appliances/genvmconfig /opt/thales/mps/livecd-mps-guest-*.vm.qcow2 > /tmp/qual_guest.xml

# Start the VM
virsh create /tmp/qual_guest.xml
