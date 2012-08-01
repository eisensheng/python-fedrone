# -*- coding: utf-8 -*-
import itertools
from collections import OrderedDict


class EnumBase(object):
    _reversed = {}
    length = -1

    @classmethod
    def reverse(cls, value):
        return cls._reversed[value]


def new_enum(enum_name, sequential=None, named=None, offset=0, stepper=None):
    named = named if named is not None else {}
    sequential = sequential if sequential is not None else []
    stepper = stepper if stepper is not None else lambda x: x

    items = itertools.chain(
        zip(sequential, (stepper(x) for x in itertools.count(start=offset))),
        named.items()
    )

    type_dict = OrderedDict(items)
    type_dict.update({
        '_reversed': dict((y, x) for x, y in type_dict.items()),
        'length': len(type_dict)
    })

    return type(enum_name, (EnumBase, ), type_dict)
