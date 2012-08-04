# -*- coding: utf-8 -*-
import struct
from fedrone.networking import SocketSender
from fedrone import ARDRONE_IP_ADDRESS, ARDRONE_COMMAND_PORT


class CommandSocket(SocketSender):
    _at_coercing_map = {
        int: lambda x: str(x),
        str: lambda x: '"%s"' % (x.encode('string_escape'), ),
        float: lambda x: str(struct.unpack('i', struct.pack('f', x))[0]),
    }

    def __init__(self):
        super(CommandSocket, self).__init__(ARDRONE_IP_ADDRESS,
                                            ARDRONE_COMMAND_PORT)

        self.sequence = 1

    def simple_at(self, command, *args):
        coerced_args = [str(self.sequence), ]

        coerce_func_finder = self._at_coercing_map.get
        coerced_args_appender = coerced_args.append
        for arg in args:
            coerce_func = coerce_func_finder(type(arg))
            coerced_args_appender(coerce_func(arg))

        self.send('AT*%s=%s\r' % (command, ','.join(coerced_args)))
        self.sequence = (self.sequence & 0xffffffff) + 1

    def at_ref(self, takeoff=False, emergency=False):
        options = 0b00010001010101000000000000000000

        if takeoff:
            options |= 0b1000000000
        if emergency:
            options |= 0b0100000000

        self.simple_at('REF', options)

    def at_pcmd(self, progressive, combined_yaw,
                left_right, front_back, altitude, yaw):

        options = 0
        if progressive:
            options |= 0b0001
        if combined_yaw:
            options |= 0b0010

        self.simple_at('PCMD', options, left_right, front_back, altitude, yaw)

    def at_ftrim(self):
        self.simple_at('FTRIM')

    def at_config(self, key, value):
        self.simple_at('CONFIG', key, value)

    def at_config_ids(self, session_id, user_id, application_id):
        self.simple_at('CONFIG_IDS', session_id, user_id, application_id)

    def at_comwdg(self):
        self.simple_at('COMWDG')

    def at_led(self, animation, freq, duration):
        self.simple_at('LED', animation, freq, duration)

    def at_anim(self, animation, duration):
        self.simple_at('ANIM', animation, duration)

    def at_zap(self, channel):
        self.simple_at('ZAP', channel)
