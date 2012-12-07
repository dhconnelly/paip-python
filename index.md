---
title: paip-python
layout: default
---

paip-python
===========

Python implementations of some of the classic AI programs from Peter Norvig's
fantastic textbook "Paradigms of Artificial Intelligence Programming."


## Overview

This is meant to be a learning resource for beginning AI programmers.  Although
PAIP is a fantastic book, it is no longer common for students to have a
background in Lisp programming, as many universities have replaced Lisp with
other languages in introductory programming and introductory artificial
intelligence courses.  It is my hope that making the programs from PAIP
available in a commonly-taught language will provide a useful hands-on resource
for beginning AI students.

The following programs are available, each with annotated source:

- [General Problem Solver][GPS], means-ends analysis problem solving
- [Eliza][], a pattern-matching psychiatrist
- [Search][], a collection of search algorithms
- [Logic][], a library for logic programming
- [Prolog][], a basic Prolog interpreter
- [Emycin][], an expert system shell
- [Othello][], some game-playing strategies for the Othello board game

Unit tests and some example applications are provided for each of these; see the
`paip/tests` and `paip/examples` directories or the links from the annotated
sources.

[GPS]: http://dhconnelly.com/paip-python/docs/paip/gps.html
[Eliza]: http://dhconnelly.com/paip-python/docs/paip/eliza.html
[Search]: http://dhconnelly.com/paip-python/docs/paip/search.html
[Logic]: http://dhconnelly.com/paip-python/docs/paip/logic.html
[Prolog]: http://dhconnelly.com/paip-python/docs/prolog.html
[Emycin]: http://dhconnelly.com/paip-python/docs/paip/emycin.html
[Othello]: http://dhconnelly.com/paip-python/docs/paip/othello.html


## Running

- You need [Python 2.7][]
- [Download][] the paip-python code.
- To run the examples: `python run_examples.py` and follow the prompts.
- To run the Prolog interpreter: `./prolog.py`.  Pass the `-h` flag for more
  details on its use and capabilities.
- To run the unit tests: `python run_tests.py`.
- To build the documentation: `python build_docs.py`.


## About

These programs were written by [Daniel Connelly][homepage] as an independent
project supervised by [Professor Ashok Goel][goel].


[homepage]: http://www.dhconnelly.com
[goel]: http://home.cc.gatech.edu/dil/3
[Download]: https://github.com/dhconnelly/paip-python/zipball/master
[Trello]: https://trello.com/board/paip-python/4f4ba053201012e46306e5f0
[Python 2.7]: http://python.org/download/releases/2.7.2/
