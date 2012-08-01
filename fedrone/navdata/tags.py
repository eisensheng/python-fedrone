# -*- coding: utf-8 -*-
from fedrone.datatypes.enum import new_enum
from fedrone.datatypes.packed import (Structure, FieldUInt32, FieldFloat,
                                      FieldSInt32, FieldStructure)
from fedrone.navdata.packedtypes import PackedVector31

from .packedtypes import PackedMatrix33


NavDataTagIds = new_enum('NavDataOptionIds',
                         ('NAVDATA_DEMO_TAG',
                          'NAVDATA_TIME_TAG',
                          'NAVDATA_RAW_MEASURES_TAG',
                          'NAVDATA_PHYS_MEASURES_TAG',
                          'NAVDATA_GYROS_OFFSETS_TAG',
                          'NAVDATA_EULER_ANGLES_TAG',
                          'NAVDATA_REFERENCES_TAG',
                          'NAVDATA_TRIMS_TAG',
                          'NAVDATA_RC_REFERENCES_TAG',
                          'NAVDATA_PWM_TAG',
                          'NAVDATA_ALTITUDE_TAG',
                          'NAVDATA_VISION_RAW_TAG',
                          'NAVDATA_VISION_OF_TAG',
                          'NAVDATA_VISION_TAG',
                          'NAVDATA_VISION_PERF_TAG',
                          'NAVDATA_TRACKERS_SEND_TAG',
                          'NAVDATA_VISION_DETECT_TAG',
                          'NAVDATA_WATCHDOG_TAG',
                          'NAVDATA_ADC_DATA_FRAME_TAG',
                          'NAVDATA_VIDEO_STREAM_TAG',
                          'NAVDATA_GAMES_TAG', ))


_registry = {}
def register_tag(tag_id):
    def __decorator(cls):
        _registry[tag_id] = cls
        return cls

    return __decorator


def get_tag_type_by_id(tag_id):
    return _registry[tag_id]


@register_tag(tag_id=NavDataTagIds.NAVDATA_DEMO_TAG)
class NavDataTagDemo(Structure):
    _struct_fields = (FieldUInt32('ctrl_state'),
                      FieldUInt32('vbat_status'),
                      FieldFloat('theta'),
                      FieldFloat('phi'),
                      FieldFloat('psi'),
                      FieldSInt32('altitude'),
                      FieldFloat('vel_x'),
                      FieldFloat('vel_y'),
                      FieldFloat('vel_z'),
                      FieldUInt32('vid_frame_count'),
                      FieldStructure('detection_camera_rot',
                                     PackedMatrix33),
                      FieldStructure('detection_camera_trans',
                                     PackedVector31),
                      FieldUInt32('detection_camera_type'),
                      FieldStructure('drone_camera_rot',
                                     PackedMatrix33),
                      FieldStructure('drone_camera_trans',
                                     PackedVector31),)


@register_tag(tag_id=0xffff)
class NavDataTagChecksum(Structure):
    _struct_fields = (FieldUInt32('ck_sum'), )
