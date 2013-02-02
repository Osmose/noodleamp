#!/usr/bin/env python
import gst


class Noodleamp(object):
    def __init__(self):
        self.player = gst.element_factory_make('playbin2', 'player')
        fakesink = gst.element_factory_make('fakesink', 'fakesink')
        self.player.set_property('video-sink', fakesink)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._handle_msg)

        self.current_song = None
        self.callbacks = []

    def stop(self):
        self.player.set_state(gst.STATE_NULL)

    def pause(self):
        self.player.set_state(gst.STATE_PAUSED)

    def play(self, song=None):
        if not song and not self.current_song:
            raise Exception('No song specified!')

        if song and song != self.current_song:
            self.stop()
            self.current_song = song
            self.player.set_state(gst.STATE_READY)
            self.player.set_property('uri', song)

        self.player.set_state(gst.STATE_PLAYING)

    def on_end(self, func):
        self.callbacks.append(func)

    def _handle_msg(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            for func in self.callbacks:
                func(self)

    def __del__(self):
        self.player.set_state(gst.STATE_NULL)
