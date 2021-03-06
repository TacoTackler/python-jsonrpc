from __future__ import absolute_import, division, unicode_literals
import sys

PY2 = sys.version_info[0] == 2
if PY2:
    import httplib
    from StringIO import StringIO  # noqa: F401

    uchr = unichr  # noqa: F821
else:
    import http.client as httplib  # noqa: F401
    from io import StringIO  # noqa: F401

    uchr = chr


def decode(string):
    """Decode a string to bytes"""
    if isinstance(string, bytes):
        result = string.decode('utf-8')
    else:
        result = string
    return result


def encode(string):
    """Encode a string to bytes"""
    if not isinstance(string, bytes):
        result = string.encode('utf-8')
    else:
        result = string
    return result
