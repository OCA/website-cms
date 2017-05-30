# -*- coding: utf-8 -*-

import base64
import requests
import mimetypes
MTYPES = mimetypes.types_map.values()
IMAGE_TYPES = [x for x in MTYPES if x.startswith('image/')]
AUDIO_TYPES = [x for x in MTYPES if x.startswith('audio/')]
VIDEO_TYPES = [x for x in MTYPES if x.startswith('video/')]


def guess_mimetype(filename_or_url):
    """Pass me a filename (or URL) and I give you a mimetype."""
    return mimetypes.guess_type(filename_or_url)[0]


class AttrDict(dict):
    """A smarter dict."""

    def __getattr__(self, k):
        """Well... get and return given attr."""
        return self[k]

    def __setattr__(self, k, v):
        """Well... set given attr."""
        self[k] = v


def download_image_from_url(url):
    """Download something from given url."""
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        return base64.encodestring(resp.content)
    return None
