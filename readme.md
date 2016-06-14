MPS	Software Qualification
==========================

Setup:
------
  - Place the __qual.tar.gz__ into the folder where	it’s going to be used.
  - Unzip __qual__ file.
  - Once the it’s uncompressed, list qual directory, and there should be 3 subdirectories (3party, common and qual)
```sh
$ ls qual
```
  - Move into 3party directory. This directory contains all package and	tools required to run the MPS Software Qualification.
```sh
$ cd 3party
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

3pary Aplications
-----------------
##### RS-485
  - In order to run RS-485 Module, an external application should be launched to send data through RS-485 devices to the QTA.
  - Open a terminal.
  - Move to Extern_Rs485 subdirectory.
```sh
$ cd 3party/Extern_Rs485
```
  - Run Extern_Rs485 -h to see the available options.
```sh
$ sudo python Extern_Rs485.py
```
  - Run Extern_Rs485
```sh
$ sudo python Extern_Rs485.py -p <port> -b <baudrate> [-m]
```

_Note that if run Extern_Rs485 with -m arg, some corrupted data will be sent._

Running
-------
  - Open a terminal.
  - Move to qta subdirectory and run thw __QTA__ application:
```sh
$ cd qual/src/qual/qta3.
$ sudo python qta.py
```
  - Open another terminal.
  - Move to QTE subdirectory and run __QTE__ application.
```sh
$ cd qual/src/qual/qte
$ sudo python qteMenu.py
```
  - A list of all modules available should diplay and from there, follow the option prompts.