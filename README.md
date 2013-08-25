# NoodleAmp

A Python-based terminal music player that uses generators as playlists.

## Setup

1. Clone the repo.
2. Install the requirements: `pip install -r requirements.txt`
3. Install gst-python. Good luck with that.

Infinite thanks to the [Mopidy](http://www.mopidy.com) team for setting up brew
recipes for installing gstreamer and being 500% more helpful than anything else
in the world on trying to get gstreamer installed on OS X. You should read
[their instructions](http://docs.mopidy.com/en/latest/installation/)
for more information.

## Usage

Now the fun part! `noodleamp.py` takes a single argument that should point to
a python file containing a generator named `playlist`.  The file
`sample_playlist.py` has an example that I will someday update to not depend on
my own file paths.

Essentially, the generator should emit absolute paths to music files, and
NoodleAmp will play them in order. This means that your generator can emit
filenames however it needs to; you could randomize songs, store ratings
and weight song frequency, or even play different songs depending on the time
of day.

## Future Work

Right now NoodleAmp is super-simple, but in the future I'd like to add:

- A better GUI
- Ability to move through the playlist and control playback
- A set of utility functions that the playlist generator can import, like
  automatically choosing a random song, extracting song metadata, etc.
- A way for playlists to add to the NoodleAmp GUI.
- Some convenient environment variables to avoid hardcoding paths into playlist
  files.

## Thanks

- I cannot thank the [Mopidy](http://www.mopidy.com) team enough for their docs.
- Erik Rose's awesome [blessings](http://pypi.python.org/pypi/blessings/)
  library for making a terminal GUI dead simple.
- Jen Fong for not getting mad at me for stealing her brand.

## License

NoodleAmp is covered by the MIT License. See LICENSE for more details.
