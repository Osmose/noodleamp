#!/usr/bin/env python
"""
Plays the musaks.
"""
import argparse
import imp
import thread
from datetime import timedelta

import pygst; pygst.require("0.10")
import gst
import gobject
from blessings import Terminal


parser = argparse.ArgumentParser(description=globals()['__doc__'],
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('playlist', help='Filename of the playlist module.')


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

        self.term = Terminal()

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

    @property
    def duration(self):
        try:
            return self.player.query_duration(gst.FORMAT_TIME, None)[0]
        except gst.QueryError:
            return 0

    @property
    def position(self):
        try:
            return self.player.query_position(gst.FORMAT_TIME, None)[0]
        except gst.QueryError:
            return 0

    @property
    def position_percent(self):
        position = self.position
        duration = self.duration
        if duration > 0:
            return position / float(duration)
        else:
            return 0

    def update_screen(self):
        term = self.term
        print term.clear
        self._render_top_bar()
        self._render_song_info()
        self._render_seek_bar()
        return True

    def init_screen(self):
        term = self.term
        print term.enter_fullscreen
        print term.hide_cursor

    def cleanup_screen(self):
        term = self.term
        print term.normal_cursor
        print term.exit_fullscreen

    def _render_top_bar(self):
        term = self.term
        with term.location(0, 0):
            print term.on_blue(' ' * term.width)
            print term.move(0, 1) + term.white_on_blue('NoodleAmp')

    def _render_song_info(self):
        term = self.term
        with term.location(2, 2):
            print term.blue('Current File: '),
            print self.current_song or 'Unknown'

    def _render_seek_bar(self):
        term = self.term
        with term.location(2, 4):
            bar_width = term.width - 7
            filled_width = int(self.position_percent * bar_width)
            empty_width = bar_width - filled_width
            print (term.blue + '<' + term.white + ('=' * filled_width) +
                   term.red + '#' + term.blue + ('.' * empty_width) + '>' +
                   term.normal)

        position_delta = format_td(timedelta(microseconds=self.position / 1000))
        duration_delta = format_td(timedelta(microseconds=self.duration / 1000))
        time_string = '{0} / {1}'.format(position_delta, duration_delta)
        with term.location(term.width - (2 + len(time_string)), 5):
            print time_string

gobject.type_register(NoodleAmp)


def format_td(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)


if __name__ == '__main__':
    args = parser.parse_args()

    playlist_filename = args.playlist
    playlist_module = imp.load_source('playlist', playlist_filename)
    playlist = playlist_module.playlist()

    main = gobject.MainLoop()
    noodleamp = NoodleAmp(main, playlist)

    noodleamp.init_screen()
    gobject.threads_init()
    gobject.timeout_add(100, noodleamp.update_screen)
    noodleamp.play_next()
    try:
        main.run()
    except KeyboardInterrupt:
        pass
    noodleamp.cleanup_screen()
