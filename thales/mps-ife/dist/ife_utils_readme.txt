Notes from ife_utils.zip release from Thales Irvine on Oct. 12, 2016:

Program Broadcom EEPROM
	1.     ife_brsw86_uwire b ife_brsw_eeprom_powerdown.bin

Program FPGA EEPROM
	1.     ife_fpga_uwire b ife_fpga_eeprom.bin

Program K60 micro controller
	1.     ife_ezport_spi p b Sidekick.afx.S19
	2.     K60 code (Sidekick.afx.S19) final version to be released by Thales Pessec

Program FPGA
	1.     In development

Program video encoder MAC address
	1.     thales_MAC_code
	2.     Generate/program first MAC address from MAC code

Program K60 MAC address
	1.     k60_MAC_code
	2.     Generate/program second MAC address from MAC code +1

Initialize video encoder module to default
	1.     fvt_z3.sh init

Check I2C devices on IFE card, including factory data I2C EEPROM
	1.     fvt_i2c.sh ife
	2.     I2C EEPROM address is 0x50 (0101_000x)
	3.     “ife_i2c_sel 0” command in the script sets FTDI GPIO control signal (bank B bit 4) to I2C multiplexer
	4.     “i2cset -y 7 0x73 0x7f” command in the script enables buses of I2C expansion chip


NOTE 2: The ife_utils_rebuilt.tgz file contains the binaries from ife_utils.zip
rebuilt with the same version of the ftdi library that's used by MAP, since the
binaries from the original package were looking for a different version of the
library.  The ife_utils_rebuilt.tgz file also contains a Makefile and updated
sources (each .c file was missing an include).
