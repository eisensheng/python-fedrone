# -*- coding: utf-8 -*-
import traceback
from collections import namedtuple

from fedrone import ARDRONE_IP_ADDRESS, ARDRONE_VIDEO_PORT
from fedrone.networking import SocketReceiver
from fedrone.video._decoder import decode_uvlc_frame


class VideoSocket(SocketReceiver):
    Image = namedtuple('Image', ('width', 'height', 'frame_nr', 'data'))

    def __init__(self):
        super(VideoSocket, self).__init__(ARDRONE_IP_ADDRESS,
                                          ARDRONE_VIDEO_PORT)

        self.image = None

    def handle_socket_data(self):
        data = self.receive()

        try:
            self.image = self.Image(*decode_uvlc_frame(data))

        except ValueError:
            traceback.print_exc()

            self.image = None
