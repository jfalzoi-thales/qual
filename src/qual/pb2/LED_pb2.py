# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: LED.proto

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
  name='LED.proto',
  package='',
  serialized_pb=_b('\n\tLED.proto\"?\n\nLEDRequest\x12\x16\n\x03led\x18\x01 \x02(\x0e\x32\t.LEDDescT\x12\x19\n\x05state\x18\x02 \x02(\x0e\x32\n.LEDStateT\"6\n\x0bLEDResponse\x12\x0f\n\x07success\x18\x01 \x02(\x08\x12\x16\n\x0c\x65rrorMessage\x18\x02 \x01(\t:\x00*E\n\x08LEDDescT\x12\x0c\n\x08LED_POST\x10\x00\x12\x14\n\x10LED_STATUS_GREEN\x10\x01\x12\x15\n\x11LED_STATUS_YELLOW\x10\x02*$\n\tLEDStateT\x12\x0b\n\x07LED_OFF\x10\x00\x12\n\n\x06LED_ON\x10\x01')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_LEDDESCT = _descriptor.EnumDescriptor(
  name='LEDDescT',
  full_name='LEDDescT',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='LED_POST', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LED_STATUS_GREEN', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LED_STATUS_YELLOW', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=134,
  serialized_end=203,
)
_sym_db.RegisterEnumDescriptor(_LEDDESCT)

LEDDescT = enum_type_wrapper.EnumTypeWrapper(_LEDDESCT)
_LEDSTATET = _descriptor.EnumDescriptor(
  name='LEDStateT',
  full_name='LEDStateT',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='LED_OFF', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LED_ON', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=205,
  serialized_end=241,
)
_sym_db.RegisterEnumDescriptor(_LEDSTATET)

LEDStateT = enum_type_wrapper.EnumTypeWrapper(_LEDSTATET)
LED_POST = 0
LED_STATUS_GREEN = 1
LED_STATUS_YELLOW = 2
LED_OFF = 0
LED_ON = 1



_LEDREQUEST = _descriptor.Descriptor(
  name='LEDRequest',
  full_name='LEDRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='led', full_name='LEDRequest.led', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='state', full_name='LEDRequest.state', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
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
  serialized_start=13,
  serialized_end=76,
)


_LEDRESPONSE = _descriptor.Descriptor(
  name='LEDResponse',
  full_name='LEDResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='LEDResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='errorMessage', full_name='LEDResponse.errorMessage', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=78,
  serialized_end=132,
)

_LEDREQUEST.fields_by_name['led'].enum_type = _LEDDESCT
_LEDREQUEST.fields_by_name['state'].enum_type = _LEDSTATET
DESCRIPTOR.message_types_by_name['LEDRequest'] = _LEDREQUEST
DESCRIPTOR.message_types_by_name['LEDResponse'] = _LEDRESPONSE
DESCRIPTOR.enum_types_by_name['LEDDescT'] = _LEDDESCT
DESCRIPTOR.enum_types_by_name['LEDStateT'] = _LEDSTATET

LEDRequest = _reflection.GeneratedProtocolMessageType('LEDRequest', (_message.Message,), dict(
  DESCRIPTOR = _LEDREQUEST,
  __module__ = 'LED_pb2'
  # @@protoc_insertion_point(class_scope:LEDRequest)
  ))
_sym_db.RegisterMessage(LEDRequest)

LEDResponse = _reflection.GeneratedProtocolMessageType('LEDResponse', (_message.Message,), dict(
  DESCRIPTOR = _LEDRESPONSE,
  __module__ = 'LED_pb2'
  # @@protoc_insertion_point(class_scope:LEDResponse)
  ))
_sym_db.RegisterMessage(LEDResponse)


# @@protoc_insertion_point(module_scope)
