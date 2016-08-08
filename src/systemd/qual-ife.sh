#!/bin/bash
echo "Qual package version is: `rpm -q --queryformat='%{VERSION}' qual-ife`"

# Install and load Microchip driver for I2C devices
if ! driver_install.sh; then
    echo "Failed to install Microchip driver"
elif ! driver_load.sh; then
    echo "Failed to load Microchip driver"
fi

# Set up device node that CLI tools expect
ln -s i2c-1 /dev/i2c-7

# Make GPIO FTDI_CONN_CTRL_I2C_SEL = low
# to set i2c mux to be controlled by x86 processor
if ! ftdibbb 0x10 0x00 > /dev/null 2>&1; then
    echo "Failed to set FTDI_CONN_CTRL_I2C_SEL"
fi

# Enable all I2C devices through I2C switch
if ! i2c 7 0x73 0x00 0x7f > /dev/null 2>&1; then
    echo "Failed to enable i2c devices"
fi

# Start Qual Test Application
cd /thales/qual/src/
PYTHONPATH=`pwd` python qual/qta/qta.py
