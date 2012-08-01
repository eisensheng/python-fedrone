# -*- coding: utf-8 -*-
import pyglet
from pyglet.app.xlib import XlibSelectDevice
from pyglet.event import EventDispatcher

from fedrone.navdata.networking import NavDataSocket


class SelectNavSocket(EventDispatcher, XlibSelectDevice):
    def __init__(self):
        super(SelectNavSocket, self).__init__()

        self._nav_socket = None

    def open(self):
        self._nav_socket = NavDataSocket()

        pyglet.app.platform_event_loop._select_devices.add(self)

    def close(self):
        if not self._nav_socket:
            return

        pyglet.app.platform_event_loop._select_devices.remove(self)
        self._nav_socket.close()
        self._nav_socket = None

    def fileno(self):
        return self._nav_socket.socket.fileno()

    def poll(self):
        return False

    def select(self):
        self._nav_socket.handle_socket_data()

        while self._nav_socket.has_more_nav_data():
            self.dispatch_event('on_drone_nav_data', 
                                self._nav_socket.next_nav_data())

SelectNavSocket.register_event_type('on_drone_nav_data')
