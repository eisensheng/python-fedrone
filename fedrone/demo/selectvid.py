# -*- coding: utf-8 -*-
import pyglet
from pyglet.app.xlib import XlibSelectDevice
from pyglet.event import EventDispatcher

from fedrone.video.networking import VideoSocket


class SelectVideoSocket(EventDispatcher, XlibSelectDevice):
    def __init__(self):
        super(SelectVideoSocket, self).__init__()

        self._video_socket = None

    def open(self):
        self._video_socket = VideoSocket()

        pyglet.app.platform_event_loop._select_devices.add(self)

    def close(self):
        if not self._video_socket:
            return

        pyglet.app.platform_event_loop._select_devices.remove(self)
        self._video_socket.close()
        self._video_socket = None

    def fileno(self):
        return self._video_socket.socket.fileno()

    def poll(self):
        return False

    def select(self):
        self._video_socket.handle_socket_data()

        if self._video_socket.image:
            self.dispatch_event('on_drone_video_frame',
                                self._video_socket.image)

SelectVideoSocket.register_event_type('on_drone_video_frame')
