MPS	Software Qualification
==========================

Setup:
------
  - Place the __qual.tar.gz__ into the folder where	it’s going to be used.
  - Unzip __qual__ file.
  - Once the it’s uncompressed, list qual directory, and there should be 3 subdirectories (3rdParty, common and qual)
```sh
$ ls qual
```
  - Move into 3rdParty directory. This directory contains all package and	tools required to run the MPS Software Qualification.
```sh
$ cd 3rdParty
```
  - Run:
```sh
$ sudo easy_install pip
```
  - To install all features, tools and packages, run:
```sh
$ sudo ./setup.sh
```

Now, the system should be ready to run the MPS Software Qualification.

Running
-------
  - Open 3 terminals.
  - In All 3 windows move to qual/src:
```sh
$ cd qual/src/
```
  - First window is used to run the simulators. 
  - Run
```sh
$ ./simulators/startsims.sh
```
  - Second window is used for QTA.
  - Log as root and run:
```sh
$ python qual/qta/qta.py
```
  - Third window is used for QTE menu.
  - Run:
```sh
$ python qual/qte/qteMenu.py -j
```
  - Can specify IP address by adding argument: -s xxx.xxx.xxx.xxx 
  - A list of all modules available should diplay and from there, follow the option prompts.

STOP QTA
--------
  - Run:
```sh
$ <ctrl> + z
$ kill -9 %1
```