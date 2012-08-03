#!/usr/bin/env python
"""
Plays the musaks.
"""
import argparse
import fcntl
import imp
import os
import sys
import termios
from collections import deque
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
        self.debug = ''

        self.song_buffer = deque()

    def _handle_msg(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.play_next()

    def pop_next_song(self):
        if self.song_buffer:
            return self.song_buffer.popleft()
        else:
            return self.playlist.next()

    def peek_next_songs(self, count=1):
        songs = []
        for k in range(count):
            if len(self.song_buffer) == k:
                self.song_buffer.append(self.playlist.next())
            songs.append(self.song_buffer[k])
        return songs

    def play_next(self):
        self.player.set_state(gst.STATE_NULL)
        try:
            self.current_song = self.pop_next_song()
        except StopIteration:
            self.main_loop.quit()
            return

        self.player.set_state(gst.STATE_READY)
        self.player.set_property('uri', 'file://{0}'.format(self.current_song))
        self.player.set_state(gst.STATE_PLAYING)
        self._render_playlist()

    def read_input(self):
        try:
            c = sys.stdin.read(1)
            self.handle_input(c)
        except IOError:
            pass
        return True

    def handle_input(self, letter):
        letter = letter.lower()
        if letter == 'p':
            self.pause()
        elif letter == 'n':
            self.play_next()

    def player_has_state(self, state):
        states = [s for s in self.player.get_state() if
                  isinstance(s, state.__class__)]
        return state in states

    def pause(self):
        if self.player_has_state(gst.STATE_PLAYING):
            self.player.set_state(gst.STATE_PAUSED)
        elif self.player_has_state(gst.STATE_PAUSED):
            self.player.set_state(gst.STATE_PLAYING)

    @property
    def is_paused(self):
        return self.player_has_state(gst.STATE_PAUSED)

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
        self._render_song_info()
        self._render_seek_bar()
        with term.location(2, term.height - 1):
            print self.debug,
        print term.move(term.height - 2, 0)
        return True

    def init_screen(self):
        term = self.term
        print term.enter_fullscreen
        print term.hide_cursor
        print term.clear
        self._render_top_bar()
        self._render_controls()
        self._render_playlist()

        self.fd = sys.stdin.fileno()

        self.oldterm = termios.tcgetattr(self.fd)
        self.newattr = termios.tcgetattr(self.fd)
        self.newattr[3] = self.newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSANOW, self.newattr)

        self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)

    def cleanup_screen(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)

        term = self.term
        print term.normal_cursor
        print term.exit_fullscreen

    def _render_top_bar(self):
        term = self.term
        with term.location(0, 0):
            print term.on_blue(' ' * term.width)
            print term.move(0, 2) + term.white_on_blue('NoodleAmp')

    def _render_song_info(self):
        term = self.term
        with term.location(2, 2):
            print term.blue('Current File: '),
            available_width = term.width - 18
            song_name = self.current_song or 'Unknown'
            format_string = '{0:<%ss}' % available_width
            print format_string.format(song_name[:available_width])

    def _render_seek_bar(self):
        term = self.term
        with term.location(2, 4):
            bar_width = term.width - 7
            filled_width = int(self.position_percent * bar_width)
            empty_width = bar_width - filled_width
            if filled_width + empty_width > bar_width:
                raise Exception('Oh noes!: %s/%s/%s' % (filled_width, empty_width, bar_width))
            print (term.blue + '<' + term.white + ('=' * filled_width) +
                   term.red + '#' + term.blue + ('.' * empty_width) + '>' +
                   term.normal)

        position_delta = format_td(timedelta(microseconds=self.position / 1000))
        duration_delta = format_td(timedelta(microseconds=self.duration / 1000))
        time_string = '{0} / {1}'.format(position_delta, duration_delta)
        with term.location(term.width - (2 + len(time_string)), 5):
            print time_string

        if self.is_paused:
            pause_str = 'Paused'
        else:
            pause_str = '      '
        with term.location(2, 5):
            print term.blue(pause_str)

    def _render_controls(self):
        term = self.term
        with term.location(2, 7):
            print '(P)lay/(P)ause (N)ext Song'

    def _render_playlist(self):
        term = self.term
        with term.location(0, 8):
            print '-' * term.width,
        with term.location(0, 9):
            songs = self.peek_next_songs(term.height - 10)
            available_width = term.width - 4
            format_string = '  {0:<%ss}' % available_width
            for song in songs:
                print format_string.format(song[:available_width])

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
    gobject.timeout_add(100, noodleamp.read_input)
    gobject.timeout_add(100, noodleamp.update_screen)
    noodleamp.play_next()
    try:
        main.run()
    except KeyboardInterrupt:
        pass
    noodleamp.cleanup_screen()
