# -*- coding: utf-8 -*-
from collections import namedtuple
import struct
import errno
import math
import os

import pyglet
from pyglet.app.xlib import XlibSelectDevice
from pyglet.event import EventDispatcher


JsEventStruct = struct.Struct('IhBB')
JsEvent = namedtuple('JsEvent', ('time', 'value', 'ev_type', 'number', ))

JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80


class GamePad(EventDispatcher, XlibSelectDevice):
    def __init__(self, filename):
        super(GamePad, self).__init__()

        self._filename = filename
        self._fileno = None

    def open(self):
        self._fileno = os.open(self._filename, os.O_RDONLY | os.O_NONBLOCK)

        pyglet.app.platform_event_loop._select_devices.add(self)

    def close(self):
        if not self._fileno:
            return

        pyglet.app.platform_event_loop._select_devices.remove(self)
        os.close(self._fileno)
        self._fileno = None

    def fileno(self):
        return self._fileno

    def poll(self):
        return False

    def select(self):
        while True:
            try:
                raw_data = os.read(self._fileno, JsEventStruct.size)

            except OSError, exc:
                if exc.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                    break

                raise exc

            event = JsEvent(*JsEventStruct.unpack(raw_data))
            if event.ev_type == JS_EVENT_BUTTON:
                self.dispatch_event('on_button', event.number, event.value)

            elif event.ev_type == JS_EVENT_AXIS:
                value = math.floor((event.value / 32767.0) * 100.0) / 100.0
                self.dispatch_event('on_axis', event.number, value)


GamePad.register_event_type('on_button')
GamePad.register_event_type('on_axis')
