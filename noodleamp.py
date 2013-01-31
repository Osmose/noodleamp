#!/usr/bin/env python
"""
Plays the musaks.
"""
import argparse
import gst
import gobject


parser = argparse.ArgumentParser(description=globals()['__doc__'],
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('file', help='File to play.')


class NoodleAmp2(object):
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


if __name__ == '__main__':
    args = parser.parse_args()

    song_filename = args.file
    noodleamp = NoodleAmp2()
    main = gobject.MainLoop()

    noodleamp.on_end(lambda n: main.quit())
    noodleamp.play('file://{0}'.format(song_filename))
    try:
        main.run()
    except KeyboardInterrupt:
        main.quit()
