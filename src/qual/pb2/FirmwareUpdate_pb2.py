# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: FirmwareUpdate.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='FirmwareUpdate.proto',
  package='mpsqual',
  serialized_pb=_b('\n\x14\x46irmwareUpdate.proto\x12\x07mpsqual\"T\n\x15\x46irmwareUpdateRequest\x12+\n\x07\x63ommand\x18\x01 \x02(\x0e\x32\x1a.mpsqual.FirmwareCommandsT\x12\x0e\n\x06reboot\x18\x02 \x02(\x08\"p\n\x16\x46irmwareUpdateResponse\x12\x0f\n\x07success\x18\x01 \x02(\x08\x12-\n\tcomponent\x18\x02 \x01(\x0e\x32\x1a.mpsqual.FirmwareCommandsT\x12\x16\n\x0c\x65rrorMessage\x18\x03 \x01(\t:\x00*\xad\x01\n\x11\x46irmwareCommandsT\x12\x0b\n\x07\x46W_BIOS\x10\x00\x12\x0b\n\x07\x46W_I350\x10\x01\x12\x18\n\x14\x46W_SWITCH_BOOTLOADER\x10\x02\x12\x16\n\x12\x46W_SWITCH_FIRMWARE\x10\x03\x12\x1b\n\x17\x46W_SWITCH_FIRMWARE_SWAP\x10\x04\x12\x14\n\x10\x46W_SWITCH_CONFIG\x10\x05\x12\x19\n\x15\x46W_SWITCH_CONFIG_SWAP\x10\x06')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_FIRMWARECOMMANDST = _descriptor.EnumDescriptor(
  name='FirmwareCommandsT',
  full_name='mpsqual.FirmwareCommandsT',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='FW_BIOS', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FW_I350', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FW_SWITCH_BOOTLOADER', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FW_SWITCH_FIRMWARE', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FW_SWITCH_FIRMWARE_SWAP', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FW_SWITCH_CONFIG', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FW_SWITCH_CONFIG_SWAP', index=6, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=234,
  serialized_end=407,
)
_sym_db.RegisterEnumDescriptor(_FIRMWARECOMMANDST)

FirmwareCommandsT = enum_type_wrapper.EnumTypeWrapper(_FIRMWARECOMMANDST)
FW_BIOS = 0
FW_I350 = 1
FW_SWITCH_BOOTLOADER = 2
FW_SWITCH_FIRMWARE = 3
FW_SWITCH_FIRMWARE_SWAP = 4
FW_SWITCH_CONFIG = 5
FW_SWITCH_CONFIG_SWAP = 6



_FIRMWAREUPDATEREQUEST = _descriptor.Descriptor(
  name='FirmwareUpdateRequest',
  full_name='mpsqual.FirmwareUpdateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='command', full_name='mpsqual.FirmwareUpdateRequest.command', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reboot', full_name='mpsqual.FirmwareUpdateRequest.reboot', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=33,
  serialized_end=117,
)


_FIRMWAREUPDATERESPONSE = _descriptor.Descriptor(
  name='FirmwareUpdateResponse',
  full_name='mpsqual.FirmwareUpdateResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='mpsqual.FirmwareUpdateResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='component', full_name='mpsqual.FirmwareUpdateResponse.component', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='errorMessage', full_name='mpsqual.FirmwareUpdateResponse.errorMessage', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=True, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=119,
  serialized_end=231,
)

_FIRMWAREUPDATEREQUEST.fields_by_name['command'].enum_type = _FIRMWARECOMMANDST
_FIRMWAREUPDATERESPONSE.fields_by_name['component'].enum_type = _FIRMWARECOMMANDST
DESCRIPTOR.message_types_by_name['FirmwareUpdateRequest'] = _FIRMWAREUPDATEREQUEST
DESCRIPTOR.message_types_by_name['FirmwareUpdateResponse'] = _FIRMWAREUPDATERESPONSE
DESCRIPTOR.enum_types_by_name['FirmwareCommandsT'] = _FIRMWARECOMMANDST

FirmwareUpdateRequest = _reflection.GeneratedProtocolMessageType('FirmwareUpdateRequest', (_message.Message,), dict(
  DESCRIPTOR = _FIRMWAREUPDATEREQUEST,
  __module__ = 'FirmwareUpdate_pb2'
  # @@protoc_insertion_point(class_scope:mpsqual.FirmwareUpdateRequest)
  ))
_sym_db.RegisterMessage(FirmwareUpdateRequest)

FirmwareUpdateResponse = _reflection.GeneratedProtocolMessageType('FirmwareUpdateResponse', (_message.Message,), dict(
  DESCRIPTOR = _FIRMWAREUPDATERESPONSE,
  __module__ = 'FirmwareUpdate_pb2'
  # @@protoc_insertion_point(class_scope:mpsqual.FirmwareUpdateResponse)
  ))
_sym_db.RegisterMessage(FirmwareUpdateResponse)


# @@protoc_insertion_point(module_scope)
