#!/usr/bin/python2
# coding=utf8

"""
Configure a VM
Derived from machine-manager/src/mm_gmma/vm.py
         and machine-manager/src/mm_common/vmconfig.py
Copyright (C) 2016 Thales Avionics, Inc.

"""

import os
import sys
import subprocess
from lxml import etree as et


# Discard the output
DEVNULL = open(os.devnull, 'wb')


class VMConfigStates(object):
    """Just an pseudo-enum class gathering all machine configuration states in single place."""
    NEW = 'new'
    ACTIVE = 'active'
    INACTIVE = 'inactive'

    def __init__(self):
        raise TypeError("Not intended to be instantiated!")


class VMDevices(object):
    """Just an pseudo-enum class gathering all machine devices in single place."""
    AUDIO        = 'audio'
    RS232        = 'rs232'
    RS485        = 'rs485'
    IFE_USB_4232 = 'ife-usb-4232'
    IFE_USB_K60  = 'ife-usb-k60'
    IFE_USB_I2C  = 'ife-usb-i2c'
    CPU_ETHERNET = 'cpu-ethernet'

    def __init__(self):
        raise TypeError("Not intended to be instantiated!")

available_vm_devices = frozenset([
    VMDevices.AUDIO, VMDevices.RS232, VMDevices.RS485,
    VMDevices.IFE_USB_4232, VMDevices.IFE_USB_K60, VMDevices.IFE_USB_I2C,
    VMDevices.CPU_ETHERNET,
])


class VMConfig(object):
    """Class representing a configuration of single VM."""

    def __init__(self, name, state=VMConfigStates.NEW, seqno=0, bank=0, last_tid=50149048542):
        self.__name = name
        self.__bank = bank
        self.state = state
        self.seqno = seqno
        self.last_tid = last_tid

        # Default values for all fields
        self.cpu = None
        self.memory = None
        self.cpu_model = "Haswell-noTSX"
        self.assigned_partitions = []
        self.assigned_devices =[]
        self.description = None
        self.custom_kernel_args = None
        self.rootfs_partition = None
        self.vlans_external = []
        self.vlans_internal = []
        self.net_vf = None
        self.boot_virtual_disk = None
        self.boot_kernel = None
        self.boot_initrd = None
        self.boot_args = None
        self.partitions= {}
        self.active_partitions = {}

    # it's very important that these fields cannot be changed
    name = property(lambda self: self.__name)
    bank = property(lambda self: self.__bank)


_xml_domain_template = '''<?xml version="1.0" encoding="UTF-8"?>
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE BY genvmconfig.
CHANGES TO IT ARE LIKELY TO BE OVERWRITTEN AND LOST.
-->

<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
  <name>FILLME</name>
  <memory unit='MiB'>FILLME</memory>
  <currentMemory unit='MiB'>FILLME</currentMemory>
  <vcpu placement='static'>FILLME</vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.0.0'>hvm</type>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu mode='custom' match='exact'>
    <model fallback='allow'>FILLME</model>
  </cpu>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='yes'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='usb' index='0' model='ich9-ehci1'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x7'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci1'>
      <master startport='0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0' multifunction='on'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci2'>
      <master startport='2'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x1'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci3'>
      <master startport='4'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x2'/>
    </controller>
    <interface type='network'>
      <mac address='52:54:00:ee:43:b8'/>
      <source network='default' bridge='virbr0'/>
      <target dev='vnet0'/>
      <model type='rtl8139'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>

    <memballoon model='none'/>
  </devices>
</domain>
'''

# mapping from VMConfig.net_vf number to physical PCI addresses
_host_vf_ifaces = {
    0: ( (0, 1, 0x10, 0), (0, 1, 0x11, 0), (0, 1, 0x12, 0), (0, 1, 0x13, 0) ),
}


class VMException(Exception):
    """ Base exception for errors raised by VM management.
        Exception contains error number and string description
    """

    def __init__(self, err_code=None, err_description=None):
        self.err_code = err_code
        self.err_description = err_description

    def __str__(self):
        if self.err_code is not None and self.err_description is not None:
            return '{0.err_code}: {0.err_description}'.format(self)
        else:
            return str(self.err_code or self.err_description or self.__class__.__name__)


def format_domain_XML(config):
    parser = et.XMLParser(remove_blank_text=True)
    template = et.fromstring(_xml_domain_template, parser)

    # helpers
    extra_disk_controllers = { }
    disk_letters = { 's': ord('a')-1, 'v': ord('a')-1 }
    def disk_devname(l):
        disk_letters[l] += 1
        return l+'d'+chr(disk_letters[l])

    def disk_target_attrs(mode):
        ret = { }
        if mode == 'sata':
            ret['bus'] = 'sata'
            ret['dev'] = disk_devname('s')
            extra_disk_controllers['sata'] = { 'type': 'sata', 'index': '0' }
        elif mode == 'virtio':
            ret['bus'] = 'virtio'
            ret['dev'] = disk_devname('v')
        elif mode == 'virtio-scsi':
            ret['bus'] = 'scsi'
            ret['dev'] = disk_devname('s')
            extra_disk_controllers['virtio-scsi'] = { 'type': 'scsi', 'index': '0', 'model': 'virtio-scsi' }
        else:
            raise VMException(-1, b"Unknown disk passthrough method {}".format(mode))
        return ret

    def pci_addr_attrs(addr_tuple):
        domain, bus, slot, function = addr_tuple
        return { 'domain':   '0x{0:04x}'.format(domain),
                 'bus':      '0x{0:02x}'.format(bus),
                 'slot':     '0x{0:02x}'.format(slot),
                 'function': '0x{0:02x}'.format(function) }

    # basic stuff
    if not config.cpu:
        raise VMException(-1, b"No CPU assigned")
    if not config.memory:
        raise VMException(-1, b"No RAM assigned")
    template.xpath('/domain/name')[0].text = config.name
    template.xpath('/domain/vcpu')[0].text = str(config.cpu)
    template.xpath('/domain/memory')[0].text = str(config.memory)
    template.xpath('/domain/currentMemory')[0].text = str(config.memory)
    template.xpath('/domain/cpu/model')[0].text = str(config.cpu_model)

    os_node = template.xpath('/domain/os')[0]
    devices_node = template.xpath('/domain/devices')[0]

    # booting
    if config.boot_virtual_disk:
        disk = et.Element('disk', type='file', device='disk')
        disk.append(et.Element('driver', name='qemu', type='qcow2'))
        disk.append(et.Element('source', file=config.boot_virtual_disk))
        disk.append(et.Element('target', **disk_target_attrs('sata')))
        disk.append(et.Element('boot', order='1'))

        devices_node.append(disk)
    else:
        if not config.boot_kernel:
            raise VMException(-1, b"Unable to boot VM: no virtual_disk/kernel specified")
        el = et.Element('kernel')
        el.text = os.path.join(config.base_path, config.boot_kernel)
        os_node.append(el)
        if config.boot_initrd:
            el = et.Element('initrd')
            el.text = os.path.join(config.base_path, config.boot_initrd)
            os_node.append(el)
        if config.boot_args:
            el = et.Element('cmdline')
            el.text = config.boot_args
            os_node.append(el)

    # disks
    for apart in config.assigned_partitions:
        pdev = config.partitions[config.active_partitions[apart]]
        # TODO check if device exists; if not, create error device

        disk = et.Element('disk', type='block', device='disk')
        disk.append(et.Element('driver', name='qemu', type='raw'))
        disk.append(et.Element('source', dev=pdev.path))
        disk.append(et.Element('target', **disk_target_attrs('virtio')))
        if pdev.ro:
            disk.append(et.Element('readonly'))

        devices_node.append(disk)

    # extra disk controllers
    for controller_params in extra_disk_controllers.values():
        devices_node.append(et.Element('controller', **controller_params))

    # network cards
    if isinstance(config.net_vf, int):
        if config.net_vf not in _host_vf_ifaces:
            raise VMException(-1, b"Unknown net VF {}".format(config.net_vf))

        for i, pci_addr in enumerate(_host_vf_ifaces[config.net_vf]):
            el = et.Element('hostdev', mode='subsystem', type='pci', managed='yes')
            addr = et.Element('address', **pci_addr_attrs(pci_addr))
            src = et.Element('source')
            src.append(addr)
            el.append(src)
            # add target address element so network cards will have predictable names inside the VM
            addr = et.Element('address', type='pci', **pci_addr_attrs((0, 0, 5+i, 0)))
            el.append(addr)
            devices_node.append(el)

    # serial console device - added to all VMs
    serial_port_idx = 0
    el = et.Element('serial', type='pty')
    el.append(et.Element('target', port=str(serial_port_idx)))
    devices_node.append(el)
    el = et.Element('console', type='pty')
    el.append(et.Element('target', type='serial', port=str(serial_port_idx)))
    devices_node.append(el)
    # check if we have proper bootarg, if not - append one
    el = os_node.find('cmdline')
    if el is not None and el.text and 'console=' not in el.text:
        el.text += ' console=ttyS{},115200n8'.format(serial_port_idx)
    serial_port_idx += 1

    # pass-through devices
    handled_devs = set()
    for dev in config.assigned_devices:
        if dev in handled_devs:
            continue # silently discard duplicate entries
        handled_devs.add(dev)

        if dev in (VMDevices.AUDIO, VMDevices.CPU_ETHERNET):
            # PCI devices
            pci_passthrough = {
                VMDevices.AUDIO:        ((0, 0, 0x1b, 0), (0, 0, 0x1b, 0)),
                VMDevices.CPU_ETHERNET: ((0, 0, 0x19, 0), (0, 0, 0x19, 0)),
            }
            host_device, vm_device = pci_passthrough[dev]
            el = et.Element('hostdev', mode='subsystem', type='pci', managed='yes')
            el.append(et.Element('driver', name='vfio'))
            addr = et.Element('address', **pci_addr_attrs(host_device))
            src = et.Element('source')
            src.append(addr)
            el.append(src)
            addr = et.Element('address', type='pci', **pci_addr_attrs(vm_device))
            el.append(addr)
            devices_node.append(el)
        elif dev in (VMDevices.RS232, VMDevices.RS485):
            # serial devices
            src_path = { VMDevices.RS232: '/dev/ttyRS232', VMDevices.RS485: '/dev/ttyRS485' }
            el = et.Element('serial', type='dev')
            el.append(et.Element('source', path=src_path[dev]))
            el.append(et.Element('target', port=str(serial_port_idx)))
            devices_node.append(el)
            serial_port_idx += 1
        elif dev in (VMDevices.IFE_USB_4232, VMDevices.IFE_USB_K60, VMDevices.IFE_USB_I2C):
            # USB devices
            usb_location = {
                VMDevices.IFE_USB_4232: '1-2',
                VMDevices.IFE_USB_K60:  '1-3',
                VMDevices.IFE_USB_I2C:  '1-7',
            }
            try:
                with open('/sys/bus/usb/devices/'+usb_location[dev]+'/devnum', 'r') as f:
                    devnum = f.readline().strip()
            except EnvironmentError:
                sys.stderr.write("Device %s not found - ignoring\n" % dev)
                #raise VMException(-1, b"Unable to read {} USB devnum (is it connected?)".format(dev))
                continue
            el = et.Element('hostdev', mode='subsystem', type='usb', managed='yes')
            addr = et.Element('address', bus='1', device=devnum)
            src = et.Element('source', startupPolicy='mandatory')
            src.append(addr)
            el.append(src)
            devices_node.append(el)
        else:
            raise VMException(-1, b"Unknown device {}".format(dev))

    return et.tostring(template.getroottree(), pretty_print=True, xml_declaration=True, encoding='UTF-8')


if __name__ == "__main__":
    # Create a VMConfig instance
    config = VMConfig("qual_guest")

    # General settings
    config.cpu = 1
    config.memory = 1024
    config.assigned_devices = [VMDevices.IFE_USB_4232, VMDevices.IFE_USB_K60, VMDevices.IFE_USB_I2C]
    config.boot_virtual_disk = sys.argv[1]

    # If running on a host that has the ens1f0 interface (i.e. running on an MPS),
    # enable the I350 ethernet interfaces and Haswell CPU model
    if subprocess.call(['ifconfig', 'ens1f0'], stdout=DEVNULL, stderr=DEVNULL) == 0:
        config.net_vf = 0
        config.cpu_model = "Haswell"

    # Create XML file from the config, and just output it - caller can redirect to file
    print format_domain_XML(config)
