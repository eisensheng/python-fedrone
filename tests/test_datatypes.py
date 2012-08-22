# -*- coding: utf-8 -*-

class TestEnum(object):
    def test_001_test_sequential(self):
        from fedrone.datatypes.enum import new_enum

        enum = new_enum('Enum', ('A', 'B', 'C'))

        assert enum.A == 0
        assert enum.B == 1
        assert enum.C == 2
