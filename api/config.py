"""yt2sp api config."""

import pathlib


# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

#songs folder
SONGS_FOLDER = pathlib.Path(__file__).resolve().parent.parent / 'songs'


