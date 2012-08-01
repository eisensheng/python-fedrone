# -*- coding: utf-8 -*-
from fedrone import ARDRONE_IP_ADDRESS, ARDRONE_NAVDATA_PORT
from fedrone.networking import SocketReceiver

from .package import NavDataPackage


class NavDataSocket(SocketReceiver):
    def __init__(self):
        super(NavDataSocket, self).__init__(ARDRONE_IP_ADDRESS,
                                            ARDRONE_NAVDATA_PORT)
        self.nav_data_cache = []

    def handle_socket_data(self):
        data = self.receive()
        data_size, total_read = len(data), 0

        while total_read < data_size:
            try:
                (bytes_read,
                 nav_data) = NavDataPackage.from_data(data[total_read:])
            except ValueError:
                break

            total_read += bytes_read
            if nav_data:
                self.nav_data_cache.append(nav_data)

    def has_more_nav_data(self):
        return len(self.nav_data_cache) > 0

    def next_nav_data(self):
        return self.nav_data_cache.pop(0)
