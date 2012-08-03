# -*- coding: utf-8 -*-
from fedrone.command.networking import CommandSocket
from fedrone.datatypes.enum import new_enum


class ArDrone(object):
    VideoChannel = new_enum('VideoChannel', ('FRONT',
                                             'BOTTOM',
                                             'LARGE_FRONT_SMALL_BOTTOM',
                                             'LARGE_BOTTOM_SMALL_FRONT',
                                             'NEXT',))

    def __init__(self):
        self.command = CommandSocket()
        self.command.at_config('general:navdata_demo', 'TRUE')

        self._speed = 1.0
        self._axis_state = [0.0, ] * 4

    def _update_moving(self):
        if max(*(abs(x) for x in self._axis_state)) < 0.01:
            self.hover()

        else:
            axis_state = map(lambda x: x * self._speed, self._axis_state)
            self.move(*axis_state)

    def config_drone(self, module, key, value):
        if isinstance(value, bool):
            value = 'TRUE' if value else 'FALSE'
        else:
            value = str(value)

        self.command.at_config('%s:%s' % (module, key), value)

    def select_camera(self, channel):
        self.config_drone('video', 'video_channel', channel)

    def flat_trim(self):
        self.command.at_ftrim()

    def watchdog(self):
        self.command.at_comwdg()

    def takeoff(self):
        self.command.at_ref(takeoff=True)

    def land(self):
        self.command.at_ref(takeoff=False)

    def emergency(self, emergency=True):
        self.command.at_ref(emergency=emergency)

    def reset(self):
        self.emergency(True)
        self.emergency(False)

    def hover(self):
        self.command.at_pcmd(False, False, 0.0, 0.0, 0.0, 0.0)

    def move(self, tilt_x, tilt_y, altitude, yaw, combined_yaw=True):
        self.command.at_pcmd(True, combined_yaw, tilt_x, tilt_y, altitude, yaw)

    @property
    def tilt_x(self):
        return self._axis_state[0]

    @tilt_x.setter
    def tilt_x(self, value):
        self._axis_state[0] = value
        self._update_moving()

    @property
    def tilt_y(self):
        return self._axis_state[1]

    @tilt_y.setter
    def tilt_y(self, value):
        self._axis_state[1] = value
        self._update_moving()

    @property
    def altitude(self):
        return self._axis_state[2]

    @altitude.setter
    def altitude(self, value):
        self._axis_state[2] = value
        self._update_moving()

    @property
    def yaw(self):
        return self._axis_state[3]

    @yaw.setter
    def yaw(self, value):
        self._axis_state[3] = value
        self._update_moving()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value
        self._update_moving()
