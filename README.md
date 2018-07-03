# gotoHeaven
Librepilot and Websocket implementation for fully autonomous quadrocopter flight


# Config of Pi (sorry only german):
Install RaspberryPI Jessi, when using Stretch the Access Point wont work!
Expand the Filesystem

sudo apt-get update

sudo apt-get upgrade

Mobile Access Point follow this tutorial:
https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md 

reboot and test connection

For me this was also needed, because DNSmasq didn't work
crontab -e
add:
@reboot dnsmasq

I also set the default IP to 192.168.178.2 and the distributed ones to .3-.23. I have done this, so I can easily connect to my home WIFI (configurated in the wpa_supplificant.conf)

Change the password of the pi.

Install dependencies to run Librepilot (on Debian): 

sudo apt-get install build-essential curl ccache debhelper git-core git-doc flex graphviz bison libudev-dev libusb-1.0-0-dev libsdl1.2-dev python libopenscenegraph-dev qt5-default qttools5-dev-tools libqt5svg5-dev qtdeclarative5-dev qml-module-qtquick-controls libqt5serialport5-dev qtmultimedia5-dev qtscript5-dev libqt5opengl5-dev qml-module-qtquick-controls qml-module-qtquick-dialogs qml-module-qtquick-xmllistmodel qml-module-qtquick-localstorage qml-module-qtquick-particles2 qml-module-qtquick-window2 qml-module-qtquick2 libosgearth-dev openscenegraph-plugin-osgearth
(https://librepilot.atlassian.net/wiki/spaces/LPDOC/pages/57671696/Linux+-+Building+and+Packaging )

Now download the sourcecode of LibrePilot.

Get the code using Git
Choose/create a dir where you want LibrePilot code:

mkdir -p ~/code
cd ~/code

Checkout code :
git clone https://bitbucket.org/librepilot/librepilot.git

Change current directory to ~/code/librepilot:
cd ~/code/librepilot

Now you can checkout code from remote Git server:
git checkout next
git pull

make all_clean
make uavobjects
make uavobjects_python_install

Install python pip to install required packeges.
sudo apt-get install python-pip
python -m pip install pyserial

sudo pip install tornado RPi.GPIO

Connect UART to Main/Flexi Port or via USB

Disable USB HID and enable USB VCP (USBTelemetry) on GCS on Librepilot GCS hardware configuration tab.
Enable Flexiport Telemetry.
Armed with yaw right 
Connect the Pi with the CC3d
Connect the batterie

Test the programs in the folder. ()
dmesg | grep tty -> Find the right device (I used S0)






