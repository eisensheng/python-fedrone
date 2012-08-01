# -*- coding: utf-8 -*-
import pprint
import sys
import errno

import pyglet
from pyglet import gl
from pyglet.window import key, Window

from fedrone.drone import ArDrone
from .gamepad import GamePad
from .selectnav import SelectNavSocket
from .selectvid import SelectVideoSocket


class ArDroneController(GamePad):
    def __init__(self, drone, filename):
        super(ArDroneController, self).__init__(filename)

        self._drone = drone

    def on_button(self, button, state):
        if not state:
            return

        if button == 0:
            self._drone.land()
        elif button == 1:
            self._drone.reset()
        elif button == 3:
            self._drone.flat_trim()
            self._drone.takeoff()

    def on_axis(self, axis, state):
        if axis == 4:
            self._drone.speed = max(0.2, abs(state) * 1.5)

        else:
            if axis == 0:
                self._drone.tilt_x = state
            elif axis == 1:
                self._drone.tilt_y = state
            elif axis == 2:
                self._drone.altitude = -state
            elif axis == 3:
                self._drone.yaw = state * 2.0


class ArDroneWindow(Window):
    def __init__(self, drone, *args, **kwargs):
        super(ArDroneWindow, self).__init__(height=240, width=320,
                                            *args, **kwargs)

        self.drone = drone
        self.drone.speed = 0.2
        self.speed = 0.05
        self.fps_display = pyglet.clock.ClockDisplay()

        self.game_pad = ArDroneController(self.drone, '/dev/input/js0')
        try:
            self.game_pad.open()
        except OSError, exc:
            if exc.errno == errno.ENOENT:
                print 'gamepad not found'
            else:
                raise exc

        self.nav_data = SelectNavSocket()
        self.nav_data.set_handlers(on_drone_nav_data=self.on_drone_nav_data)
        self.nav_data.open()

        self.video_stream = SelectVideoSocket()
        self.video_stream.set_handlers(
            on_drone_video_frame=self.on_drone_video_frame
        )
        self.video_stream.open()

    def _set_speed(self, speed):
        self.speed = speed

    def on_drone_video_frame(self, video_frame):
        image = pyglet.image.ImageData(width=video_frame.width,
                                       height=video_frame.height,
                                       format='RGBA',
                                       data=video_frame.data)

        self.switch_to()
        image.blit(0.0, 0.0)
        self.flip()

    def on_drone_nav_data(self, nav_data):
        sys.stdout.write('\x1B[2J')
        pprint.pprint(dict(nav_data.tags[0][0]._asdict()), stream=sys.stdout)
        sys.stdout.flush()

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, height, 0, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def on_key_press(self, symbol, modifiers):
        key_handlers = {
            key._1: lambda: self._set_speed(0.1),
            key._2: lambda: self._set_speed(0.2),
            key._3: lambda: self._set_speed(0.3),
            key._4: lambda: self._set_speed(0.4),
            key._5: lambda: self._set_speed(0.5),
            key._6: lambda: self._set_speed(0.6),
            key._7: lambda: self._set_speed(0.7),
            key._8: lambda: self._set_speed(0.8),
            key._9: lambda: self._set_speed(0.9),
            key._0: lambda: self._set_speed(1.0),
            key.UP: lambda: setattr(self.drone, 'altitude', self.speed),
            key.DOWN: lambda: setattr(self.drone, 'altitude', -self.speed),
            key.W: lambda: setattr(self.drone, 'tilt_y', -self.speed),
            key.S: lambda: setattr(self.drone, 'tilt_y', self.speed),
            key.LEFT: lambda: setattr(self.drone, 'tilt_x', -self.speed),
            key.RIGHT: lambda: setattr(self.drone, 'tilt_x', self.speed),
            key.A: lambda: setattr(self.drone, 'yaw', -self.speed),
            key.D: lambda: setattr(self.drone, 'yaw', self.speed),
            key.RETURN: lambda: self.drone.takeoff(),
            key.SPACE: lambda: self.drone.land(),
            key.BACKSPACE: lambda: self.drone.reset(),
        }

        handler = key_handlers.get(symbol)
        if handler:
            handler()
            return pyglet.event.EVENT_HANDLED

        return pyglet.event.EVENT_UNHANDLED

    def on_key_release(self, symbol, modifiers):
        key_handlers = {
            key.UP: lambda: setattr(self.drone, 'altitude', 0.0),
            key.DOWN: lambda: setattr(self.drone, 'altitude', 0.0),
            key.W: lambda: setattr(self.drone, 'tilt_y', 0.0),
            key.S: lambda: setattr(self.drone, 'tilt_y', 0.0),
            key.LEFT: lambda: setattr(self.drone, 'tilt_x', 0.0),
            key.RIGHT: lambda: setattr(self.drone, 'tilt_x', 0.0),
            key.A: lambda: setattr(self.drone, 'yaw', 0.0),
            key.D: lambda: setattr(self.drone, 'yaw', 0.0),
        }

        handler = key_handlers.get(symbol)
        if handler:
            handler()
            return pyglet.event.EVENT_HANDLED

        return pyglet.event.EVENT_UNHANDLED

    def on_deactivate(self):
        self.drone.hover()

    def on_draw(self):
        pass

    def watchdog_timer(self, delta_s=None):
        self.drone.watchdog()

    def run(self):
        pyglet.clock.schedule_interval(self.watchdog_timer, 0.1)

        sys.stdout.write('\x1B[?25l')
        try:
            pyglet.app.run()
        finally:
            sys.stdout.write('\x1B[?25h')


def main():
    drone = ArDrone()
    window = ArDroneWindow(drone)
    window.run()


if __name__ == '__main__':
    main()
