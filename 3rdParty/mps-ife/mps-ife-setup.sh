#!/bin/sh

# Install and load Microchip driver for I2C devices
if ! driver_install.sh; then
        echo "Failed to install Microchip driver"
elif ! driver_load.sh; then
        echo "Failed to load Microchip driver"
fi

# Assign sidekick IP address
ifconfig eno1 192.168.0.64
ifconfig eno1:sk 10.1.69.69
