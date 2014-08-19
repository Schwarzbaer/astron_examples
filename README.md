astron_examples
===============

IMPORTANT!
==========

This project depends on features in https://github.com/TheCheapestPixels/panda3d

Examples
========

01\_simple\_example - The most minimalistic MMO
-----------------------------------------------

All this demo does is to create a small map and allow an arbitrary number of clients, all sharing the same credentials (username guest, password guest), to log in, move about the map and see each other. To use it:
* start astrond with the given astrond.yml
* start simple\_example\_server.py
* start two or more simple\_example\_client.py
FIXME: Add detailed description of what happens when you start the server/clients

02\_sqlite\_db - The minimum of persistence
-------------------------------------------

This example elaborates on 01 by adding proper user accounts; before starting everything as before, run simple\_example\_add\_user (with a --username <name>) to create an account.

FIXME: Currently, this example is non-functional. My intention is that avatars (specifically, their positions and heading) now get saved in the DB, so when you log in again, your avatar gets recreated at the same position where you logged out the last time.

Notation
========
TODO is a feature request. FIXME is a known bug. Both are in comments in the relevant files, except that I'm using this too as a general notebook, me lazy bastard:

FIXME
* simple\_example
  * allow for setting loglevel
* sqlite\_db
  * Finish changing the setup process to CREATE/ACTIVATE DOs instead of .generate()

TODO
* simple_example
  * Clean up the 22 FIXMEs left.
* full_example
  * Persistent accounts (database)
  * Resetting state after crash
  * Multiple shards (AI repos)
  * High Availability and load balancing UberDOGs and AI shards
  * client downloads / updates asset files
* Advanced examples
  * Smoothed object movement
  * Advanced security checks





