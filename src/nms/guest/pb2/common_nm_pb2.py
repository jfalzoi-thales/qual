# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common_nm.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='common_nm.proto',
  package='',
  serialized_pb=_b('\n\x0f\x63ommon_nm.proto\"&\n\x08Property\x12\x0b\n\x03key\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\"=\n\x0c\x45rrorMessage\x12\x12\n\nerror_code\x18\x01 \x02(\r\x12\x19\n\x11\x65rror_description\x18\x02 \x02(\t\"W\n\tValueResp\x12\x0f\n\x07success\x18\x01 \x02(\x08\x12\x1b\n\x08keyValue\x18\x02 \x02(\x0b\x32\t.Property\x12\x1c\n\x05\x65rror\x18\x03 \x01(\x0b\x32\r.ErrorMessage\"\x91\x01\n\rMessageHeader\x12\x10\n\x08msg_name\x18\x01 \x02(\t\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65stination\x18\x03 \x01(\t\x12\x14\n\x0csequence_nbr\x18\x04 \x01(\x04\x12\x16\n\x0eretransmission\x18\x05 \x01(\x08\x12\x1b\n\x08\x61\x64\x64_data\x18\x06 \x03(\x0b\x32\t.Property')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PROPERTY = _descriptor.Descriptor(
  name='Property',
  full_name='Property',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='Property.key', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='Property.value', index=1,
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
  serialized_start=19,
  serialized_end=57,
)


_ERRORMESSAGE = _descriptor.Descriptor(
  name='ErrorMessage',
  full_name='ErrorMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='error_code', full_name='ErrorMessage.error_code', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error_description', full_name='ErrorMessage.error_description', index=1,
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
  serialized_start=59,
  serialized_end=120,
)


_VALUERESP = _descriptor.Descriptor(
  name='ValueResp',
  full_name='ValueResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='ValueResp.success', index=0,
      number=1, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='keyValue', full_name='ValueResp.keyValue', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error', full_name='ValueResp.error', index=2,
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
  serialized_start=122,
  serialized_end=209,
)


_MESSAGEHEADER = _descriptor.Descriptor(
  name='MessageHeader',
  full_name='MessageHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='msg_name', full_name='MessageHeader.msg_name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source', full_name='MessageHeader.source', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='destination', full_name='MessageHeader.destination', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sequence_nbr', full_name='MessageHeader.sequence_nbr', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='retransmission', full_name='MessageHeader.retransmission', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='add_data', full_name='MessageHeader.add_data', index=5,
      number=6, type=11, cpp_type=10, label=3,
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
  serialized_start=212,
  serialized_end=357,
)

_VALUERESP.fields_by_name['keyValue'].message_type = _PROPERTY
_VALUERESP.fields_by_name['error'].message_type = _ERRORMESSAGE
_MESSAGEHEADER.fields_by_name['add_data'].message_type = _PROPERTY
DESCRIPTOR.message_types_by_name['Property'] = _PROPERTY
DESCRIPTOR.message_types_by_name['ErrorMessage'] = _ERRORMESSAGE
DESCRIPTOR.message_types_by_name['ValueResp'] = _VALUERESP
DESCRIPTOR.message_types_by_name['MessageHeader'] = _MESSAGEHEADER

Property = _reflection.GeneratedProtocolMessageType('Property', (_message.Message,), dict(
  DESCRIPTOR = _PROPERTY,
  __module__ = 'common_nm_pb2'
  # @@protoc_insertion_point(class_scope:Property)
  ))
_sym_db.RegisterMessage(Property)

ErrorMessage = _reflection.GeneratedProtocolMessageType('ErrorMessage', (_message.Message,), dict(
  DESCRIPTOR = _ERRORMESSAGE,
  __module__ = 'common_nm_pb2'
  # @@protoc_insertion_point(class_scope:ErrorMessage)
  ))
_sym_db.RegisterMessage(ErrorMessage)

ValueResp = _reflection.GeneratedProtocolMessageType('ValueResp', (_message.Message,), dict(
  DESCRIPTOR = _VALUERESP,
  __module__ = 'common_nm_pb2'
  # @@protoc_insertion_point(class_scope:ValueResp)
  ))
_sym_db.RegisterMessage(ValueResp)

MessageHeader = _reflection.GeneratedProtocolMessageType('MessageHeader', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEHEADER,
  __module__ = 'common_nm_pb2'
  # @@protoc_insertion_point(class_scope:MessageHeader)
  ))
_sym_db.RegisterMessage(MessageHeader)


# @@protoc_insertion_point(module_scope)
