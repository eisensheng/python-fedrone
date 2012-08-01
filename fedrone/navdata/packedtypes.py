# -*- coding: utf-8 -*-
from fedrone.datatypes.packed import Structure, FieldFloat


class PackedMatrix33(Structure):
    _struct_fields = (FieldFloat('m11'), FieldFloat('m12'), FieldFloat('m13'),
                      FieldFloat('m21'), FieldFloat('m22'), FieldFloat('m23'),
                      FieldFloat('m31'), FieldFloat('m32'), FieldFloat('m33'))


class PackedVector31(Structure):
    _struct_fields = (FieldFloat('x'), FieldFloat('y'), FieldFloat('z'), )
