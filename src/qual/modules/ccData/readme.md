# Carrier Card Data Module
The Carrier Card Data module reads and writes carrier card inventory information, which
is stored as VPD (Vital Product Data) information on the I350 Ethernet controller.
 
##### Carrier Card Data Request:
The Carrier Card Data Request Message is sent by the TE to program or read back the carrier card
inventory data.  The inventory data is stored in VPD (Vital Product Data) area in the EEPROM
on the Intel I350 Ethernet controller.

The CarrierCardDataRequest has the following structure:

  - enum RequestTypeT requestType = 1;
  - repeated Property values = 2;

The supported values for requestType are:

  - READ = 0;
  - WRITE = 1;
  - ERASE = 2;
  - WRITE_PROTECT = 3;

The Property field has the following structure:

  - required string key = 1;
  - required string value = 2;

##### Carrier Card Data Response:
The Carrier Card Data Response Message is sent by the MPS to indicate success or failure
of Carrier Card Data requests, and return any carrier card inventory values that have been
programmed.

The CarrierCardDataResponse has the following structure:

  - required bool success = 1;
  - optional ErrorMsg error = 2;
  - optional bool writeProtected = 3;
  - repeated Property values = 4;

The ErrorMsg field has the following structure:

  - required uint32 error_code = 1;
  - optional string description = 2;
  
The defined values for error_code used by this module are:

  - FAILURE_INVALID_MESSAGE = 1000;
  - FAILURE_INVALID_KEY     = 1001;
  - FAILURE_INVALID_VALUE   = 1002;
  - FAILURE_WRITE_PROTECT_DISABLED = 1003;
  - FAILURE_READ_FAILED     = 1004;
  - FAILURE_WRITE_FAILED    = 1005;

##### READ Request:
When requestType is READ, the module will read the VPD from the I350 EEPROM, parse the VPD
if present, and return a list of inventory items parsed from the VPD that was read.
If a problem occurred while attempting to read the VPD, the success field in the response
will be set to False, and the error field will be present.  Otherwise, the success field in
the response will be set to True, and values will contain the inventory items.  Note that
if the VPD area is unprogrammed, the success  field in the response will still be set to True,
but the values list will be empty.

##### WRITE Request:
When requestType is WRITE, the module will encode inventory items into VPD format and program
the VPD area of the I350 EEPROM with the new values.  The values field of the request should
contain key/value pairs containing the inventory information that is to be programmed.
The following table lists the supported keys for the values field, along with the maximum
length for the value of that key:

   Key                |Max. Length
   -------------------|-----------
   part_number        |    24
   serial_number      |    24
   revision           |     8
   manufacturer_pn    |    24
   manufacturing_date |     8
   manufacturer_name  |    24
   manufacturer_cage  |     8

If any error occurs during a WRITE operation, no data is written to the EEPROM,
and the success field in the response will be set to False and the error field
will be present.  Possible reasons for failure include:

  - An invalid key was present in the request, 
  - A value in the request exceeded the maximum length defined for that value
  - The EEPROM was write-protected
  - A problem occurred while attempting to write to the EEPROM

If all keys and values are valid, and the write to EEPROM is successful,
the response will have the success field set to True, and the values list
will contain all of the VPD entries programmed in EEPROM after the operation.
 
Note: If a WRITE request is issued on a system which already has VPD information
programmed, the new data will be used to update the existing data. If a VPD entry
is present on the system and not present in the request, the existing VPD entry will
still be present after the WRITE operation.  This allows part of the data to be
written at one time, and additional data to be added later.  However, this behavior
means that if you are not writing all fields, and want to be sure that no old data
is kept, you should first issue an ERASE request, and then write your data with a
WRITE request.

##### ERASE Request:
When requestType is ERASE, the module will erase the entire VPD block in EEPROM.
If a problem occurred while attempting to read the VPD, the success field in the response
will be set to False, and the error field will be present.  Otherwise, the success field in
the response will be set to True.

##### WRITE_PROTECT Request:
When requestType is WRITE_PROTECT, the system will write-protect the EEPROM so that
no further changes can be made.  _THIS IS A ONE-TIME OPERATION_: once the EEPROM
write protection is enabled, it cannot be disabled.  For that reason, the module
can be configured to disable the write protect function, so that it is not
accidentally triggered during testing (see Configuration, below).

If the write protect function is disabled, the response will have the success
field set to False, and error.error_code will be set to FAILURE_WRITE_PROTECT_DISABLED.
If no data has been programmed (determined by checking thatpart_number and serial_number
values are programmed), the write protect request will not proceed, and the response will have
the success field set to False, and error.error_code will be set to FAILURE_INVALID_VALUE.
If the write protect operation fails for some other reason, the response will have
the success field set to False, and error.error_code will be set to FAILURE_WRITE_FAILED.
If the write protect operation succeeds, the response will have the success field
set to True.

##### Configuration:
There are two configuration parameters for the Carrier Card Data module.  The
config file section is [CarrierCardData], and the parameters are as follows:

  - ethDevice: The Linux Ethernet device name of the I350.  On a target system, it
    will be something like enp2s0f0.  This parameter may also be set to the
    special value TEST_FILE, in which case the module will read and write the VPD
    to a local file named vpd.bin instead of trying to access the Ethernet device.
  - enableWriteProtect: This boolean parameter controls whether the write protect
    function can be used.  The default value is False.

##### Implementation note - VPD Keywords:
VPD, as defined in the PCI specification, uses two-character keywords to identify fields
in the VPD binary format.  While the Carrier Card Data request and response messages use
inventory keys such as part_number and manufacturing_date, in the VPD that is written to
the EEPROM these keys are mapped to two-character VPD keywords.  Where the VPD specification
defines a keyword that matches the meaning of an inventory key, a defined keyword from
the specification is used.  Otherwise, "vendor-specific" keywords (first character is
'V', second character is defined by the vendor) are used.

The following table shows how the inventory keys are mapped to VPD keywords, along
with the description of each VPD keyword from the PCI specification.

   Inventory Key      |VPD Keyword| VPD Description
   -------------------|-----------|-------------------------
   part_number        |    PN     | Part Number
   serial_number      |    SN     | Serial Number
   revision           |    EC     | Engineering Change Level
   manufacturer_pn    |    VP     | Vendor-defined 'P'
   manufacturing_date |    VD     | Vendor-defined 'D'
   manufacturer_name  |    VN     | Vendor-defined 'N'
   manufacturer_cage  |    VC     | Vendor-defined 'C'
