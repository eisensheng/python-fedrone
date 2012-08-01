# -*- coding: utf-8 -*-
import struct
from collections import namedtuple


class StructureBaseField(object):
    __slots__ = ('name', )
    struct_format = 'x'

    def __init__(self, name):
        self.name = name


class FieldStructure(StructureBaseField):
    __slots__ = ('name',
                 'struct_format')

    def __init__(self, name, structure):
        super(FieldStructure, self).__init__(name)

        self.name = []
        for field in structure._struct_fields:
            field_names = field.name
            if not isinstance(field_names, (tuple, list, )):
                field_names = [field_names, ]

            for field_name in field_names:
                self.name.append('{0}__{1}'.format(name, field_name))

        self.struct_format = structure._raw_unpacker_fmt


class FieldUint16(StructureBaseField):
    struct_format = 'H'


class FieldSInt32(StructureBaseField):
    struct_format = 'i'


class FieldUInt32(StructureBaseField):
    struct_format = 'I'


class FieldFloat(StructureBaseField):
    struct_format = 'f'


class StructureMeta(type):
    def __new__(mcs, *args, **kwargs):
        cls_name, cls_bases, cls_dict = args[:3]

        field_names, struct_formats = [], []
        for field in cls_dict['_struct_fields']:
            field_name = field.name
            if not isinstance(field_name, (tuple, list, )):
                field_name = [field_name]
            field_names.extend(field_name)

            struct_formats.append(field.struct_format)

        unpacker_fmt = ''.join(struct_formats)
        cls_dict.update({
            '_raw_unpacker_fmt': unpacker_fmt,
            '_raw_unpacker': struct.Struct('=' + unpacker_fmt),
        })

        tuple_type = namedtuple('{0}Tuple'.format(cls_name), field_names)
        cls_bases = (tuple_type, ) + cls_bases

        return super(StructureMeta, mcs).__new__(
            mcs, cls_name, cls_bases, cls_dict, *args[3:], **kwargs
        )


class Structure(object):
    __metaclass__ = StructureMeta
    __slots__ = ()

    _struct_fields = ()
    _raw_unpacker = struct.Struct('')

    @classmethod
    def _make_from_buffer(cls, buffer, offset=0):
        return cls(*cls._raw_unpacker.unpack_from(buffer, offset))
