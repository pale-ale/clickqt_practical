Technical Documentation
=======================

==========
Frameworks
==========
This section displays all the frameworks used to realise clickQt.

click
-----
The Command Line Interface Creation Kit is a python package to create Command Line Interfaces with as little code as necessary. Click makes the
development of Command Line Interfaces easier and quicker. Click was used to set up the command line interfaces that are later on
transated into the UI of clickQt, that is realised with Qt-widgets by PySide6.

PySide6
-------
PySide6 is python package that provides access to the Qt6.0+ framework of C++ and offers a broad variety of Qt-widgets for text input, numerical inputs or even date input.
Each standard click type is mapped to a certain Qt-widget, which is realised as a seperate UI class. The widgets are used to set
the values of the parameters of a specific command. These values are parsed to the click command for its execution.

Here's a list of the most relevant classes and what they do:

1. :class:`clickqt.core.gui.GUI`
