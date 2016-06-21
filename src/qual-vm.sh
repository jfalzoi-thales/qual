rm /sbin/mpsinst-makeraid
rm /etc/udev/rules.d/80*
rm /etc/udev/rules.d/95*
cd /thales/qual/src/
simulator/startsims.sh
PYTHONPATH=`pwd` python qual/qta/qta.py
