paip-python
===========

Python implementations of some of the classic AI programs from Peter Norvig's
fantastic textbook "Paradigms of Artificial Intelligence Programming."

About
-----

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

[GPS]: http://dhconnelly.github.com/paip-python/docs/paip/gps.html
[Eliza]: http://dhconnelly.github.com/paip-python/docs/paip/eliza.html
[Search]: http://dhconnelly.github.com/paip-python/docs/paip/search.html
[Logic]: http://dhconnelly.github.com/paip-python/docs/paip/logic.html
[Prolog]: http://dhconnelly.github.com/paip-python/docs/prolog.html
[Emycin]: http://dhconnelly.github.com/paip-python/docs/paip/emycin.html
[Othello]: http://dhconnelly.github.com/paip-python/docs/paip/othello.html

Getting Started
---------------

Get the source code from [GitHub](https://github.com/dhconnelly/paip-python) or
just [download](https://github.com/dhconnelly/paip-python/zipball/master) the
latest version.

Also make sure you have [Python 2.7](http://python.org/download/releases).

- To run the examples: `python run_examples.py` and follow the prompts.
- To run the Prolog interpreter: `./prolog.py`.  Pass the `-h` flag for more
  details on its use and capabilities.
- To run the unit tests: `python run_tests.py`.
- To build the documentation: `python build_docs.py`.

Contributing
------------

- fork on [GitHub](https://github.com/dhconnelly/paip-python)
- write code in `paip/`
- add unit tests in `paip/tests`
- make sure all tests pass: `python run_tests.py`
- send me a pull request

Author
------

These programs were written by [Daniel Connelly](http://dhconnelly.com) at
Georgia Tech as an independent project supervised by [Professor Ashok
Goel](http://home.cc.gatech.edu/dil/3).
