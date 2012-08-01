# -*- coding: utf-8 -*-
from fedrone.video.networking import VideoSocket
import select


vid_sock = VideoSocket()
while True:
    rdy_r, _, _ = select.select([vid_sock.socket], [], [])

    if vid_sock.socket in rdy_r:
        vid_sock.handle_socket_data()
        if not vid_sock.image:
            continue

        print (vid_sock.image.width,
               vid_sock.image.height,
               vid_sock.image.frame_nr)
