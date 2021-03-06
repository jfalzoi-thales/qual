# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: HDDS_API.proto

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
  name='HDDS_API.proto',
  package='HDDS_API',
  serialized_pb=_b('\n\x0eHDDS_API.proto\x12\x08HDDS_API\"&\n\x08Property\x12\x0b\n\x03key\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\"=\n\x0c\x45rrorMessage\x12\x12\n\nerror_code\x18\x01 \x02(\r\x12\x19\n\x11\x65rror_description\x18\x02 \x02(\t\"i\n\tValueResp\x12\x0f\n\x07success\x18\x01 \x02(\x08\x12$\n\x08keyValue\x18\x02 \x02(\x0b\x32\x12.HDDS_API.Property\x12%\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x16.HDDS_API.ErrorMessage\"\x15\n\x06GetReq\x12\x0b\n\x03key\x18\x01 \x03(\t\"f\n\x07GetResp\x12#\n\x06values\x18\x01 \x03(\x0b\x32\x13.HDDS_API.ValueResp\x12\x0f\n\x07success\x18\x02 \x02(\x08\x12%\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x16.HDDS_API.ErrorMessage\",\n\x06SetReq\x12\"\n\x06values\x18\x01 \x03(\x0b\x32\x12.HDDS_API.Property\"f\n\x07SetResp\x12#\n\x06values\x18\x01 \x03(\x0b\x32\x13.HDDS_API.ValueResp\x12\x0f\n\x07success\x18\x02 \x02(\x08\x12%\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x16.HDDS_API.ErrorMessage*\xad\x01\n\x07\x45rrCode\x12\x1c\n\x17\x46\x41ILURE_INVALID_MESSAGE\x10\xe8\x07\x12\x18\n\x13\x46\x41ILURE_INVALID_KEY\x10\xe9\x07\x12\x1a\n\x15\x46\x41ILURE_INVALID_VALUE\x10\xea\x07\x12\x1c\n\x17\x46\x41ILURE_SET_UNSUPPORTED\x10\xeb\x07\x12\x17\n\x12\x46\x41ILURE_GET_FAILED\x10\xec\x07\x12\x17\n\x12\x46\x41ILURE_SET_FAILED\x10\xed\x07')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_ERRCODE = _descriptor.EnumDescriptor(
  name='ErrCode',
  full_name='HDDS_API.ErrCode',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='FAILURE_INVALID_MESSAGE', index=0, number=1000,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILURE_INVALID_KEY', index=1, number=1001,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILURE_INVALID_VALUE', index=2, number=1002,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILURE_SET_UNSUPPORTED', index=3, number=1003,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILURE_GET_FAILED', index=4, number=1004,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILURE_SET_FAILED', index=5, number=1005,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=516,
  serialized_end=689,
)
_sym_db.RegisterEnumDescriptor(_ERRCODE)

ErrCode = enum_type_wrapper.EnumTypeWrapper(_ERRCODE)
FAILURE_INVALID_MESSAGE = 1000
FAILURE_INVALID_KEY = 1001
FAILURE_INVALID_VALUE = 1002
FAILURE_SET_UNSUPPORTED = 1003
FAILURE_GET_FAILED = 1004
FAILURE_SET_FAILED = 1005



_PROPERTY = _descriptor.Descriptor(
  name='Property',
  full_name='HDDS_API.Property',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='HDDS_API.Property.key', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='HDDS_API.Property.value', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=28,
  serialized_end=66,
)


_ERRORMESSAGE = _descriptor.Descriptor(
  name='ErrorMessage',
  full_name='HDDS_API.ErrorMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='error_code', full_name='HDDS_API.ErrorMessage.error_code', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error_description', full_name='HDDS_API.ErrorMessage.error_description', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=68,
  serialized_end=129,
)


_VALUERESP = _descriptor.Descriptor(
  name='ValueResp',
  full_name='HDDS_API.ValueResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='HDDS_API.ValueResp.success', index=0,
      number=1, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='keyValue', full_name='HDDS_API.ValueResp.keyValue', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error', full_name='HDDS_API.ValueResp.error', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=131,
  serialized_end=236,
)


_GETREQ = _descriptor.Descriptor(
  name='GetReq',
  full_name='HDDS_API.GetReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='HDDS_API.GetReq.key', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=238,
  serialized_end=259,
)


_GETRESP = _descriptor.Descriptor(
  name='GetResp',
  full_name='HDDS_API.GetResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='HDDS_API.GetResp.values', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='success', full_name='HDDS_API.GetResp.success', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error', full_name='HDDS_API.GetResp.error', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=261,
  serialized_end=363,
)


_SETREQ = _descriptor.Descriptor(
  name='SetReq',
  full_name='HDDS_API.SetReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='HDDS_API.SetReq.values', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=365,
  serialized_end=409,
)


_SETRESP = _descriptor.Descriptor(
  name='SetResp',
  full_name='HDDS_API.SetResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='HDDS_API.SetResp.values', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='success', full_name='HDDS_API.SetResp.success', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error', full_name='HDDS_API.SetResp.error', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=411,
  serialized_end=513,
)

_VALUERESP.fields_by_name['keyValue'].message_type = _PROPERTY
_VALUERESP.fields_by_name['error'].message_type = _ERRORMESSAGE
_GETRESP.fields_by_name['values'].message_type = _VALUERESP
_GETRESP.fields_by_name['error'].message_type = _ERRORMESSAGE
_SETREQ.fields_by_name['values'].message_type = _PROPERTY
_SETRESP.fields_by_name['values'].message_type = _VALUERESP
_SETRESP.fields_by_name['error'].message_type = _ERRORMESSAGE
DESCRIPTOR.message_types_by_name['Property'] = _PROPERTY
DESCRIPTOR.message_types_by_name['ErrorMessage'] = _ERRORMESSAGE
DESCRIPTOR.message_types_by_name['ValueResp'] = _VALUERESP
DESCRIPTOR.message_types_by_name['GetReq'] = _GETREQ
DESCRIPTOR.message_types_by_name['GetResp'] = _GETRESP
DESCRIPTOR.message_types_by_name['SetReq'] = _SETREQ
DESCRIPTOR.message_types_by_name['SetResp'] = _SETRESP
DESCRIPTOR.enum_types_by_name['ErrCode'] = _ERRCODE

Property = _reflection.GeneratedProtocolMessageType('Property', (_message.Message,), dict(
  DESCRIPTOR = _PROPERTY,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.Property)
  ))
_sym_db.RegisterMessage(Property)

ErrorMessage = _reflection.GeneratedProtocolMessageType('ErrorMessage', (_message.Message,), dict(
  DESCRIPTOR = _ERRORMESSAGE,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.ErrorMessage)
  ))
_sym_db.RegisterMessage(ErrorMessage)

ValueResp = _reflection.GeneratedProtocolMessageType('ValueResp', (_message.Message,), dict(
  DESCRIPTOR = _VALUERESP,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.ValueResp)
  ))
_sym_db.RegisterMessage(ValueResp)

GetReq = _reflection.GeneratedProtocolMessageType('GetReq', (_message.Message,), dict(
  DESCRIPTOR = _GETREQ,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.GetReq)
  ))
_sym_db.RegisterMessage(GetReq)

GetResp = _reflection.GeneratedProtocolMessageType('GetResp', (_message.Message,), dict(
  DESCRIPTOR = _GETRESP,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.GetResp)
  ))
_sym_db.RegisterMessage(GetResp)

SetReq = _reflection.GeneratedProtocolMessageType('SetReq', (_message.Message,), dict(
  DESCRIPTOR = _SETREQ,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.SetReq)
  ))
_sym_db.RegisterMessage(SetReq)

SetResp = _reflection.GeneratedProtocolMessageType('SetResp', (_message.Message,), dict(
  DESCRIPTOR = _SETRESP,
  __module__ = 'HDDS_API_pb2'
  # @@protoc_insertion_point(class_scope:HDDS_API.SetResp)
  ))
_sym_db.RegisterMessage(SetResp)


# @@protoc_insertion_point(module_scope)
