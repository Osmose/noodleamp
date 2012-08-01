#!/usr/bin/env python
"""
Plays the musaks.
"""
import argparse
import imp
import thread
from time import sleep

import pygst
pygst.require("0.10")
import gst
import gobject
gobject.threads_init()

from blessings import Terminal

parser = argparse.ArgumentParser(description=globals()['__doc__'],
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('playlist', help='Filename of the playlist.')


class NoodleAmp(gst.Bin):
    def __init__(self, main_loop, playlist):
        self.__gobject_init__()
        self.main_loop = main_loop
        self.playlist = playlist

        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._handle_msg)

        self.current_song = None

    def _handle_msg(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.play_next()

    def play_next(self):
        try:
            self.current_song = self.playlist.next()
        except StopIteration:
            self.main_loop.quit()
            return

        self.player.set_state(gst.STATE_READY)
        self.player.set_property('uri', 'file://{0}'.format(self.current_song))
        self.player.set_state(gst.STATE_PLAYING)

gobject.type_register(NoodleAmp)

if __name__ == '__main__':
    args = parser.parse_args()

    playlist_filename = args.playlist
    playlist_module = imp.load_source('playlist', playlist_filename)
    playlist = playlist_module.playlist()

    main = gobject.MainLoop()
    noodleamp = NoodleAmp(main, playlist)

    def update_screen():
        term = Terminal()
        with term.fullscreen():
            while True:
                print term.clear
                with term.location(0, 0):
                    print term.on_blue(' ' * term.width)
                    print term.move(0, 1) + term.white_on_blue('NoodleAmp')
                with term.location(2, 2):
                    print term.blue('Current File: ') + noodleamp.current_song
                    sleep(0.5)

    thread.start_new_thread(update_screen, ())
    noodleamp.play_next()
    main.run()
