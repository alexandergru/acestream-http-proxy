acestream-http-proxy
====================

Ace stream to HTTP proxy
It's very simple and ugly.
It's based on blocking sockets and should be rewritten right after the initial commit.

"acestream" is a folder with basic class to communicate with Ace Stream server,
and "ace.py" is a basic multi-threaded web-proxy.

Right now it supports only Ace Stream Content ID.

## How to use ##
Run: python2 ace.py

Open http://127.0.0.1:8000/acestream_content_id in your video player
