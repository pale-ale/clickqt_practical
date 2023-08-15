Technical Documentation
=======================

This is a short overview of all the important design decisions concerning the used frameworks, paired with the most crucial components of
clickQt in case you want to make changes to the theme or application behaviour yourself..

==========
Frameworks
==========
This section displays all the frameworks used to realise clickQt.

click
-----
The Command Line Interface Creation Kit is a python package to create Command Line Interfaces with as little code as necessary. Click makes the
development of Command Line Interfaces easier and quicker. Click was used to set up the command line interfaces that are later on
translated into the UI of clickQt, that is realised with Qt-widgets from PySide6.

.. code-block:: python

    import click

    @click.command()
    @click.option('--count', default=1, help='Number of greetings.')
    @click.option('--name', prompt='Your name',
                  help='The person to greet.')
    def hello(count, name):
        """Simple program that greets NAME for a total of COUNT times."""
        for x in range(count):
            click.echo(f"Hello {name}!")

    if __name__ == '__main__':
        hello()

PySide6
-------
PySide6 is a Python package that provides access to the Qt6.0+ framework of C++ and offers a variety of Qt-widgets for different kinds of inputs.
Each standard click type is mapped to a certain Qt-widget, which is realised as a separate UI class. The widgets are used to set
the values of the parameters of a specific command. These values are passed to the click command for its execution.

=====================
Most important method
=====================

The most important method of clickQt is the qtgui_from_click() method, whose concrete documentation can be found here: :mod:`clickqt.core.core`.

| To summarize the importance of this function:

The user calls this central function to create the gui from a Command Line Interface that has been built in click by parsing the click command to this function, but
qtgui_from_click allows one to set additional parameters like application name or application icon. In addition to that, the function sets the actual layout of the GUI, e.g. the size, theme, etc. to be used for the layout.

=================
Important classes
=================
This section displays all the important classes used in clickQt together with all the important methods.

1. :class:`clickqt.core.gui.GUI`
This class is responsible for creating the widgets that are needed for the constructed depending on the parameter types of the commands presented in the Command Line Interface
together with the general layout of the GUI, providing basic utilities of a GUI, i.e a Run Button.

The most important methods in this class are:

#. __init()
    * The constructor of the GUI class setting all necessary widgets for the basic usage of the GUI:
        #. The main widget containing all sub widgets
        #. Run Button
        #. Terminal Output
#. construct()
    * This method is responsible for resizing the GUI and centering the window based on the window data of te device.
#. create_widget()
    * This method is responsible for mapping the parameter to the widget based on the paremter type.

2. :class:`clickqt.core.control.Control`
This class is responsible for handling the execution of the command presented on the GUI like parsing the command parameters to the click command such that it can be executed correctly.

The most important methods in this class are:

#. __init()
    * The constructor of the Control class linking the necessary GUI widgets with functions that are invoked if the widgets are clicked on.
    * The constructor also sets up the necessary datastructures to manage the widgets that are present in the window.
    * The constructor calls the parse() function to go either create the widgets of a simple command or to go through the subcommands of the grouped command in order to create the widgets for these subcommands.

#. parse()
    * This method is responsible to determine how the widgets for the command should be created, either through the parse_cmd_group() function or through the parse_cmd() function.

#. parse_cmd()
    * This method parses through every option and argument of the command for a simple QTabwidget

 #. parse_cmd_group()
    * This method creates for every subcommand a QTabwidget and these subcommands are parsed seperately for the widget creation.

3. :class:`clickqt.widgets.basewidget.BaseWidget`
This is the base class for the widgets that are used for the mapping of click types to these widgets.

The most important methods in this class are:
#. __init()
    * The constructor the BaseWidget class setting the layout and the widget type for the specific click parameter type.
    * It is important to state that the widget_type is set before the __init() function, which is supposed to be a Qt-widget if one writes a new class inheriting from this BaseWidget class.
