import imp
import threading
from collections import deque
from urlparse import urlparse, urlunparse

import gobject
import gst
from gst.extend.discoverer import Discoverer

gobject.threads_init()


class EventThread(threading.Thread):
    def run(self):
        self.main_loop = gobject.MainLoop()
        self.main_loop.run()


class NoodleAmp(object):
    def __init__(self):
        self.player = gst.element_factory_make('playbin2', 'player')
        fakesink = gst.element_factory_make('fakesink', 'fakesink')
        self.player.set_property('video-sink', fakesink)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self._handle_message)

        self.current_song = None
        self.metadata = []
        self.playlist = None
        self.callbacks = []

        self.event_thread = EventThread()
        self.event_thread.daemon = True
        self.event_thread.start()

    @property
    def is_playing(self):
        return self._has_state(gst.STATE_PLAYING)

    def stop(self):
        self.player.set_state(gst.STATE_NULL)

    def pause(self):
        self.player.set_state(gst.STATE_PAUSED)

    def unpause(self):
        self.player.set_state(gst.STATE_PLAYING)

    def play(self, url):
        # Try loading as a module first.
        module = None
        try:
            module = imp.load_source('playlist', url)
        except:
            pass

        if module:
            self.playlist = Playlist(module.playlist())
            url = self.playlist.next()

        if url:
            d = Discoverer(url)
            d.connect('discovered', self._discovered)
            d.discover()

            url = self._fix_url(url)
            self.stop()
            self.current_song = url
            self.player.set_state(gst.STATE_READY)
            self.player.set_property('uri', url)

        self.player.set_state(gst.STATE_PLAYING)

    def status_song(self):
        return self.current_song

    def song_length(self):
        if self.is_playing:
            duration = self.player.query_duration(gst.FORMAT_TIME, None)[0]
            if duration == -1:
                return "00:00"
            return self._convert_ns(duration)
        return "00:00"

    def song_title(self):
        return self.metadata['tags']['title']

    def song_artist(self):
        return self.metadata['tags']['artist']

    def song_progress(self):
        if self.is_playing:
            duration = self.player.query_position(gst.FORMAT_TIME, None)[0]
            if duration == -1:
                return "00:00"
            return self._convert_ns(duration)
        return "00:00"

    # Borrowed code from: http://pygstdocs.berlios.de/pygst-tutorial/seeking.html
    def _convert_ns(self, t):
        s, ns = divmod(t, 1000000000)
        m, s = divmod(s, 60)

        if m < 60:
            return "%02i:%02i" % (m, s)
        else:
            h, m = divmod(m, 60)
            return "%i:%02i:%02i" % (h, m, s)

    def on_end(self, func):
        self.callbacks.append(func)
        return func

    def _discovered(self, discoverer, ismedia):
        self.metadata = discoverer.__dict__

    def _handle_message(self, bus, msg):
        t = msg.type
        if t == gst.MESSAGE_ERROR:
            print "Error playing file: %s" % self.current_song
        elif t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        else:
            return
        if self.playlist:
            try:
                return self.play(self.playlist.next())
            except StopIteration:
                pass
        for func in self.callbacks:
            func(self)

    def _fix_url(self, url):
        parsed = urlparse(url)
        if not parsed.scheme:
            parsed = list(parsed)
            parsed[0] = 'file'
            url = urlunparse(parsed)
        return url

    def _has_state(self, state):
        states = [s for s in self.player.get_state() if
                  isinstance(s, state.__class__)]
        return state in states

    def __del__(self):
        self.player.set_state(gst.STATE_NULL)


class Playlist(object):
    def __init__(self, generator):
        self.generator = generator
        self.cache = deque()

    def __getitem__(self, key):
        max_key = key.stop if isinstance(key, slice) else key
        if key.stop >= len(self.cache):
            try:
                self._update_cache_to(max_key)
            except StopIteration:
                raise IndexError
        return self.cache[key]

    def __iter__(self):
        return self

    def _update_cache_to(self, key):
        for _ in range(key):
            self.cache.append(self.generator.next())

    def next(self):
        if not self.cache:
            self._update_cache_to(1)
        return self.cache.popleft()
