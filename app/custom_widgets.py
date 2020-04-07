import tkinter as tk
from tkinter import ttk
import tkinter.constants as tkc
from tkinter import filedialog

import colors

"""
This file contains a collection of custom widgets to collect data from user.
"""


class FieldWidget(tk.Frame):
    def __init__(self, master, label_text):
        """
        Instantiates this frame with a Label and Entry Widget.
        :param master: The Parent Widget
        :param label_text: The Initial text for the label.
        """
        # init self as a tk.Frame
        tk.Frame.__init__(self, master, bg=colors.JAMA_HILO_SILVER)

        # Default value
        self.value = None

        # Create a Label
        self.label_string_var = tk.StringVar(master, label_text)
        self.label = ttk.Label(self,
                               textvariable=self.label_string_var,
                               width=20,
                               anchor=tkc.E,
                               background=colors.JAMA_HILO_SILVER)

        # Pack the Frame
        self.label.pack(side=tkc.LEFT)

    def get_value(self):
        return self.value

    def set_value(self, value):
        pass


class StringFieldWidget(FieldWidget):
    """
    This class Represents a Frame containing a Label and an Entry Widget, that can be used to get String data from the
    user.
    """

    def __init__(self, master, label_text, show=None):
        """
        Instantiates this frame with a Label and Entry Widget.
        :param master: The Parent Widget
        :param label_text: The Initial text for the label.
        :param show: optional parameter used to obfuscate entered text. i.e. set show='*' to get password as "********"
        """
        # init self as a tk.Frame
        FieldWidget.__init__(self, master, label_text)

        # Create a String Entry Widget
        self.value = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.value, width=30, show=show)

        # Pack the Frame
        self.entry.pack(side=tkc.LEFT)

    def get_value(self):
        return self.value.get()

    def set_value(self, string_value):
        self.value.set(string_value)


class DirectoryChooserFieldWidget(StringFieldWidget):
    """
    This class represents a directory chooser field
    """

    def __init__(self, master, label_text):
        # Init parent
        StringFieldWidget.__init__(self, master, label_text)

        # Add a button that calls a file chooser and sets the result to the field value
        self.dir_chooser_button = ttk.Button(self, text="Select", command=self.choose_file)

        # Pack it
        self.dir_chooser_button.pack(side=tkc.LEFT)

    def choose_file(self):
        directory = filedialog.askdirectory()
        if directory is not None and directory != '':
            self.set_value(directory)


class RadioButtonFieldWidget(FieldWidget):
    """
    This Class will create a group of radio buttons for the form
    """

    def __init__(self, master, label_text, options):
        """
        Builds an entry widget of radio buttons
        :param master: The owning component.
        :param label_text: The Field Label
        :return:
        """
        # Init the field widget
        FieldWidget.__init__(self, master, label_text)
        self.value = tk.IntVar()
        self.value.set(0)

        for option_number, option_label in enumerate(options):
            # Create a RadioButton for label:
            rb = tk.Radiobutton(self,
                                text=option_label,
                                variable=self.value,
                                value=option_number,
                                background=colors.JAMA_HILO_SILVER)
            rb.pack(side=tkc.LEFT)

    def get_value(self):
        return self.value.get()

    def set_value(self, value):
        try:
            value = int(value)
            self.value.set(value)
        except ValueError:
            pass
