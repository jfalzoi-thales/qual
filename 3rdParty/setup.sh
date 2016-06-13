#!/bin/bash
clear
echo
echo "****************************************************************************************"
echo "*  This scrpits installs and copies all external packages, tool and features required  *"
echo "****************************************************************************************"
echo

## Directories
MAIN_WD=$(pwd)
BIN_WD="/usr/local/bin"
LIB_WD="/usr/local/lib"

## Variables
STATUS="Status:\n\t"
PACKAGE="Package status: "

INSTALLED="installed."
NOTINSTALLED="not installed."
MISSING="missing"

###############################################
## Export Python local package               ##
cd ..
cd "src"
PYTHONPATH=$(pwd)
export PYTHONPATH
cd $MAIN_WD

echo -e $STATUS $PYTHONPATH" added."
echo "-----------------------------------------------------------------------------------"

###############################################
## Install: Parallel Memory Bandwidth (PMBW) ##
PMBW="pmbw"

if [ -a $BIN_WD"/"$PMBW ]
then
    echo -e $STATUS $PMBW $INSTALLED
elif [ -a $MAIN_WD"/"$PMBW ]
then
    cp $MAIN_WD"/"$PMBW $BIN_WD
    echo -e $STATUS $PMBW $INSTALLED
else
    ## if for some reason the executable do not exits, compile the source code and install
    cd $MAIN_WD"/"$PMBW"/src"
    ./configure
    make
    make install
    echo -e $STATUS $PMBW $INSTALLED
fi
cd $MAIN_WD
echo "-----------------------------------------------------------------------------------"

##############################################
## Install: FIO                             ##
FIO="fio"
FIO_PKG="fio-2.1.10-1.el7.rf.x86_64.rpm"

cd $MAIN_WD"/"$FIO

INST=$(rpm -qa | grep "fio-2.1.10-1.el7.rf.x86_64")

if [[ $INST == "" ]]
then
    rpm -iv $FIO_PKG
    echo -e $STATUS $FIO $INSTALLED
else
    echo -e $STATUS $FIO $INSTALLED
fi
cd $MAIN_WD
echo "-----------------------------------------------------------------------------------"

###############################################
## Install: Google Protocol Buffers library, ##
GPB="gpb"
GPB_PKG="protobuf-2.6.1-py2.7.egg"

INST=$(pip list | grep "protobuf")

if [[ $INST == "" ]]
then
    cd $MAIN_WD"/"$GPB
    easy_install -iv $GPB_PKG
    cd $MAIN_WD
    echo -e $STATUS "ProtoBuf" $INSTALLED
else
    echo -e $STATUS "ProtoBuf" $INSTALLED
fi

echo "-----------------------------------------------------------------------------------"

###############################################
## Install: iPerf                            ##
IPERF="iperf3"
IPERF_RPM="iperf3-3.1.3-1.el7.x86_64.rpm"

INST=$(rpm -qa | grep "iperf3-3.1.3-1.el7.x86_64")

if [[ $INST == "" ]]
then
    cd $MAIN_WD"/"$IPERF
    rpm -iv $IPERF_RPM
    cd $MAIN_WD
    echo -e $STATUS $IPERF $INSTALLED
else
    echo -e $STATUS $IPERF $INSTALLED
fi
echo "-----------------------------------------------------------------------------------"

###############################################
## Install: Lookbusy                         ##
LOOKBUSY="lookbusy"
LOOKBUSY_DIR="lookbusy/lookbusy-1.4"

if [ -a $BIN_WD"/"$LOOKBUSY ]
then
    echo -e $STATUS $LOOKBUSY $INSTALLED
else
    cd $MAIN_WD"/"$LOOKBUSY_DIR
    cp $LOOKBUSY $BIN_WD
    cd $MAIN_WD
    echo -e $STATUS $LOOKBUSY $INSTALLED
fi
echo "-----------------------------------------------------------------------------------"

###############################################
## Install: pySerial                         ##
PYSERIAL="pyserial"
PYSERIAL_PKG="pyserial-2.6-5.el7.noarch.rpm"

INST=$(rpm -qa | grep "pyserial-2.6-5.el7.noarch")

if [[ $INST == "" ]]
then
    cd $MAIN_WD"/pyserial"
    rpm -iv $PYSERIAL_PKG
    cd $MAIN_WD
    echo -e $STATUS $PYSERIAL $INSTALLED
else
    echo -e $STATUS $PYSERIAL $INSTALLED
fi
echo "-----------------------------------------------------------------------------------"

###############################################
## Install: ZMQ                         ##
ZMQ="ZMQ"

OPENPGM_PKG="openpgm-5.2.122-2.el7.x86_64.rpm"
ZMQ_PKG="zeromq3-3.2.5-1.el7.x86_64.rpm"
PYZMQ_PKG="pyzmq-15.2.0-py2.7-linux-x86_64.egg"

cd $MAIN_WD"/zmq"

INST=$(rpm -qa | grep "openpgm-5.2.122-2.el7.x86_64")

if [[ $INST == "" ]]
then
    sudo rpm -Uv $OPENPGM_PKG
    echo -e $STATUS "OpenGM" $INSTALLED
else
    echo -e $STATUS "OpenGM" $INSTALLED
fi

INST=$(rpm -qa | grep "zeromq3-3.2.5-1.el7.x86_64")

if [[ $INST == "" ]]
then
    sudo rpm -Uv $ZMQ_PKG
    echo -e $STATUS "ZeroMQ" $INSTALLED
else
    echo -e $STATUS "ZeroMQ" $INSTALLED
fi


INST=$(pip list | grep "pyzmq")

if [[ $INST == "" ]]
then
    easy_install $PYZMQ_PKG
    echo -e $STATUS "PyZMQ" $INSTALLED
else
    echo -e $STATUS "PyZMQ" $INSTALLED
fi

cd $MAIN_WD
echo "-----------------------------------------------------------------------------------"

echo
echo "****************************************************************************************"
echo "*                                         DONE                                         *"
echo "****************************************************************************************"
echo
###############################################