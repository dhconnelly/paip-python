# paip-python

Python implementations of the classic AI programs from Peter Norvig's fantastic
textbook "Paradigms of Artificial Intelligence Programming."

## Overview

This is meant to be a learning resource for beginning AI programmers.  It is no
longer common for students to have a background in Lisp programming, as many
universities have replaced Lisp with other languages in introductory programming
and introductory artificial intelligence courses.  It is my hope that making the
programs from PAIP available in a commonly-taught language will provide a useful
hands-on resource for beginning AI students.

I am writing these programs while reading through PAIP, so consider this a work
in progress.  Additionally, I am not at this time focusing on the end-of-chapter
exercises, which typically propose extensions to the programs to avoid various
limitations.  I hope that these Python programs are clean translations and don't
try to force Lisp idioms onto Python.

## Running

- You need [Python 2.7](http://python.org/download/releases/2.7.2/).  I
  recommend downloading one of the binary installers if you're running Windows or
  Mac OS X.

- Download the paip-python code
  [as a zip file](https://github.com/dhconnelly/paip-python/zipball/master).

- The programs are all runnable from the command line.  For example, to run the
  General Problem Solver on the provided Blocks World problem, do the following:
    * cd ~/Downloads/paip-python
    * cd gps
    * python gps.py blocks.json

- Without Unix command-line access, run the IDLE Python IDE that is
  automatically installed by the binary installers, and when the Python shell
  loads, do the following:
    * import sys
    * sys.path.append('/path/to/paip-python/gps')
    * import gps
    * gps.main(['/path/to/paip-python/gps/blocks.json'])

## About

These programs were written by [Daniel Connelly](http://www.dhconnelly.com) as
an independent project supervised by [Professor Ashok Goel](http://home.cc.gatech.edu/dil/3) at Georgia Tech.
