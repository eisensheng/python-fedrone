# -*- coding: utf-8 -*-
import struct
from StringIO import StringIO
from collections import namedtuple, defaultdict

from .tags import get_tag_type_by_id


# FLY MASK : (0) ardrone is landed,
#            (1) ardrone is flying
#
# VIDEO MASK : (0) video disable,
#              (1) video enable
#
# VISION MASK : (0) vision disable,
#               (1) vision enable
#
# CONTROL ALGO (0) euler angles control,
#              (1) angular speed control
#
# ALTITUDE CONTROL ALGO : (0) altitude control inactive
#                         (1) altitude control active
#
# USER feedback : Start button state
#
# Control command ACK : (0) None,
#                       (1) one received
#
# Firmware file is good (1)
#
# Firmware update is newer (1)
#
# Firmware update is ongoing (1)
#
# Navdata demo : (0) All navdata,
#                (1) only navdata demo
#
# Navdata bootstrap : (0) options sent in all or demo mode,
#                     (1) no navdata options sent
#
# Motor status : (0) Ok,
#                (1) Motors problem
#
# Communication lost : (1) com problem,
#                      (0) Com is ok
#
# VBat low : (1) too low,
#            (0) Ok
#
# User Emergency Landing : (1) User EL is ON,
#                          (0) User EL is OFF
#
# Timer elapsed : (1) elapsed,
#                 (0) not elapsed
#
# Angles : (0) Ok,
#          (1) out of range
#
# Ultrasonic sensor : (0) Ok,
#                     (1) deaf
#
# Cutout system detection : (0) Not detected,
#                           (1) detected
#
# PIC Version number OK : (0) a bad version number,
#                         (1) version number is OK
#
# ATCodec thread ON : (0) thread OFF
#                     (1) thread ON
#
# Navdata thread ON : (0) thread OFF
#                     (1) thread ON
#
# Video thread ON : (0) thread OFF
#                   (1) thread ON
#
# Acquisition thread ON : (0) thread OFF
#                         (1) thread ON
#
# CTRL watchdog : (1) delay in control execution (> 5ms),
#                 (0) control is well scheduled
#
# ADC Watchdog : (1) delay in uart2 dsr (> 5ms),
#                (0) uart2 is good
#
# Communication Watchdog : (1) com problem,
#                          (0) Com is ok
#
# Emergency landing : (0) no emergency,
#                     (1) emergency

DroneState = namedtuple('NavdataPackage', ('fly_mask',
                                           'video_mask',
                                           'vision_mask',
                                           'control_mask',
                                           'altitude_mask',
                                           'user_feedback_start'
                                           'command_mask',
                                           'fw_file_mask',
                                           'fw_ver_mask',
                                           'fw_upd_mask',
                                           'navdata_demo_mask',
                                           'navdata_bootstrap',
                                           'motors_mask',
                                           'com_lost_mask',
                                           'vbat_low',
                                           'user_el',
                                           'timer_elapsed',
                                           'angles_out_of_range',
                                           'ultrasound_mask',
                                           'cutout_mask',
                                           'pic_version_mask',
                                           'atcodec_thread_on',
                                           'navdata_thread_on',
                                           'video_thread_on',
                                           'acq_thread_on',
                                           'ctrl_watchdog_mask',
                                           'adc_watchdog_mask',
                                           'com_watchdog_mask',
                                           'emergency_mask', ))


PackageHeaderStruct = struct.Struct('IIII')
PackageHeader = namedtuple('NavDataPackageHeader', ('magic',
                                                    'drone_state',
                                                    'seq_nr',
                                                    'vision_flag'))

TagMetaStruct = struct.Struct('HH')


class StructStringIO(StringIO):
    def read_struct(self, struct_def):
        return struct_def.unpack(self.read(struct_def.size))


class NavDataPackage(object):
    def __init__(self, header=None, tags=None):
        if not header:
            drone_state = DroneState(*([None, ] * len(DroneState._fields)))
            header = PackageHeader(magic=None,
                                   drone_state=drone_state,
                                   seq_nr=0,
                                   vision_flag=0)
        self.header = header

        if not tags:
            tags = {}
        self.tags = tags

    @classmethod
    def from_data_extract_header(cls, data_buf):
        package_header = PackageHeader(
            *data_buf.read_struct(PackageHeaderStruct)
        )._asdict()

        flags = package_header['drone_state']
        fields = dict((field, bool((flags >> idx) & 1))
                      for idx, field in enumerate(DroneState._fields))
        package_header['drone_state'] = DroneState(**fields)

        return PackageHeader(**package_header)

    @classmethod
    def from_data_extract_tags(cls, data_buf):
        tags = defaultdict(list)
        tags_field_len = len(data_buf.getvalue())
        while data_buf.tell() < tags_field_len:
            tag_id, size = data_buf.read_struct(TagMetaStruct)
            if size < TagMetaStruct.size:
                raise RuntimeError('strange message')

            tag_data = data_buf.read(size - TagMetaStruct.size)
            try:
                tag_type = get_tag_type_by_id(tag_id)
            except KeyError:
                tag = tag_data
            else:
                tag = tag_type._make_from_buffer(tag_data)

            tags[tag_id].append(tag)

            if tag_id == 0xffff:
                break

        return tags

    @classmethod
    def from_data(cls, data):
        if len(data) < PackageHeaderStruct.size:
            raise ValueError('insufficient data provided')
        data_buf = StructStringIO(data)

        header = cls.from_data_extract_header(data_buf)
        if header.magic != 0x55667788:
            return 1, None

        tags = cls.from_data_extract_tags(data_buf)

        return data_buf.tell(), cls(header, tags)
