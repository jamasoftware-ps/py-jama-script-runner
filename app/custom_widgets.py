import tkinter as tk
from tkinter import ttk
import tkinter.constants as tkc
from tkinter import Text
from tkinter import messagebox

import colors
import app_constants as const

from py_jama_rest_client.client import JamaClient

"""
This file contains a collection of custom widgets.
"""


class ScriptSettingsPanel(tk.LabelFrame):

    def __init__(self, master):
        tk.LabelFrame.__init__(self, master, text=const.SCRIPT_SETTINGS_PANEL_LABEL, bg=colors.JAMA_HILO_SILVER)

        # Set back reference
        self.parent = master

        # Add custom fields here
        self.project_id_field = FieldEntryFrame(self, "Project ID:")
        self.baseline_id_field = FieldEntryFrame(self, "Baseline ID:")

        # Pack the Frame
        self.project_id_field.pack(fill=tkc.X)
        self.baseline_id_field.pack(fill=tkc.X)


class ClientSettingsPanel(tk.LabelFrame):
    """
    This class is handles all input of Jama Client connection details
    """

    def __init__(self, master):
        # Initialize the LabelFrame
        tk.LabelFrame.__init__(self, master, text=const.CLIENT_PANEL_LABEL, bg=colors.JAMA_HILO_SILVER)

        # Set a parent reference
        self.parent = master

        # Setup connection panel
        # Prompt for URL info
        self.url_field = FieldEntryFrame(self, const.URL_LABEL)

        # Prompt for Auth Mode
        self.auth_mode_field = AuthModeSelector(self)

        # Create Username Field
        self.username_field = FieldEntryFrame(self, const.USERNAME)
        self.password_field = FieldEntryFrame(self, const.PASSWORD, show='*')

        # Pack the Frame
        self.url_field.pack(fill=tkc.X)
        self.auth_mode_field.pack(fill=tkc.X)
        self.username_field.pack(fill=tkc.X)
        self.password_field.pack(fill=tkc.X)

    def get_client(self):
        """This method does the following:
            1) Reads in the values in the Client Settings panel
            2) Validates the fields.  i.e. trim whitespace; add https:// to url fields missing it.
            3) Create a JamaClient instance and attempt to make a connection to it.
            4) Returns the new JamaClient. or None if
        """
        try:
            # Read values
            url = self.url_field.entry_string_var.get().strip().lower()
            # Get those pesky backslashes out
            while url.endswith('/'):
                url = url[0:len(url) - 1]
            # If http or https method not specified in the url then add it now.
            if not (url.startswith('https://') or url.startswith('http://')):
                url = 'https://' + url
            self.url_field.entry_string_var.set(url)

            if self.auth_mode_field.auth_mode.get() == AuthModeSelector.AUTH_MODE_BASIC:
                use_oauth = False
            else:
                use_oauth = True
            username = self.username_field.entry_string_var.get().strip()
            password = self.password_field.entry_string_var.get().strip()
            # Create the client
            jama_client = JamaClient(url, credentials=(username, password), oauth=use_oauth)
            # Attempt a connection
            jama_client.get_available_endpoints()
            # No Exception?  ok it will probably work; return the client.
            return jama_client

        except Exception as e:
            messagebox.showerror("Unable to connect", "Please check your client settings.")
            print(e)
            raise e


class AuthModeSelector(tk.Frame):
    """
    This Class represents the Auth mode radio button selectors
    """
    AUTH_MODE_BASIC = 0
    AUTH_MODE_OAUTH = 1

    def __init__(self, master: ClientSettingsPanel):
        # Initialize the Frame
        tk.Frame.__init__(self, master, bg=colors.JAMA_HILO_SILVER)

        # Parent reference
        self.parent = master

        # Create a Label
        self.label = ttk.Label(self, text=const.AUTH_MODE_LABEL, width=20, anchor=tkc.E,
                               background=colors.JAMA_HILO_SILVER)

        # Create a Integer variable to bind to
        self.auth_mode = tk.IntVar(self.parent.parent)

        # Create a RadioButton for each Auth mode type: Basic / OAuth
        self.auth_mode_basic_rb = tk.Radiobutton(self,
                                                 text=const.BASIC_AUTH_LABEL,
                                                 variable=self.auth_mode,
                                                 value=AuthModeSelector.AUTH_MODE_BASIC,
                                                 command=self.auth_mode_change,
                                                 background=colors.JAMA_HILO_SILVER)

        self.auth_mode_oauth_rb = tk.Radiobutton(self,
                                                 text=const.OAUTH_LABEL,
                                                 variable=self.auth_mode,
                                                 value=AuthModeSelector.AUTH_MODE_OAUTH,
                                                 command=self.auth_mode_change,
                                                 background=colors.JAMA_HILO_SILVER)
        # Pack the frame
        self.label.pack(side=tkc.LEFT)
        self.auth_mode_basic_rb.pack(side=tkc.LEFT)
        self.auth_mode_oauth_rb.pack(side=tkc.LEFT)

    def auth_mode_change(self):
        """
        Sets the display text on the USER ID and USER SECRET fields when the Auth mode is changed.
        :return:
        """
        if self.auth_mode.get() == AuthModeSelector.AUTH_MODE_BASIC:
            self.parent.username_field.label_string_var.set(const.USERNAME)
            self.parent.password_field.label_string_var.set(const.PASSWORD)
        else:
            self.parent.username_field.label_string_var.set(const.CLIENT_ID)
            self.parent.password_field.label_string_var.set(const.CLIENT_SECRET)


class FieldEntryFrame(tk.Frame):
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
        tk.Frame.__init__(self, master, bg=colors.JAMA_HILO_SILVER)

        # Create a Label
        self.label_string_var = tk.StringVar(master, label_text)
        self.label = ttk.Label(self,
                               textvariable=self.label_string_var,
                               width=20,
                               anchor=tkc.E,
                               background=colors.JAMA_MOONSHOT_GOLD)

        # Create a Entry Widget
        self.entry_string_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.entry_string_var, width=30, show=show)

        # Pack the Frame
        self.label.pack(side=tkc.LEFT)
        self.entry.pack(side=tkc.LEFT)


class ResultsPanel(tk.LabelFrame):
    def __init__(self, master):
        # Init LabelFrame superclass
        tk.LabelFrame.__init__(self, master, text=const.RESULT_PANEL_LABEL, bg=colors.JAMA_HILO_SILVER)

        # Set parent reference
        self.parent = master

        # Add a Text widget to display results.  Set it to disabled so that the User may not interact with it.
        self.result_text = Text(self, state=tkc.DISABLED, background=colors.JAMA_HILO_SILVER)

        # Add a scrollbar for results
        self.result_scrollbar = ttk.Scrollbar(self, orient=tkc.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=self.result_scrollbar.set)

        # Pack the Widget
        self.result_scrollbar.pack(side=tkc.RIGHT, fill=tkc.Y)
        self.result_text.pack(fill=tkc.BOTH, expand=tkc.TRUE)

    def append_message(self, msg):
        self.result_text.configure(state=tkc.NORMAL)
        self.result_text.insert(tkc.END, msg)
        self.result_text.see(tkc.END)
        self.result_text.configure(state=tkc.DISABLED)

    def clear(self):
        self.result_text.configure(state=tkc.NORMAL)
        self.result_text.delete('1.0', tkc.END)
        self.result_text.configure(state=tkc.DISABLED)


class ExecutePanel(tk.Frame):
    """
    This Panel contains an execute button and is where the user starts the script execution.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master, bg=colors.JAMA_HILO_SILVER)
        # Set parent reference
        self.parent = master

        # Create the Execute button
        self.execute_button = ttk.Button(self, text=const.EXECUTE_BUTTON_TEXT,
                                         command=self.parent.execute_button_command)

        # Create a label to display the current status.
        self.status_label = ttk.Label(self,
                                      textvariable=self.parent.status,
                                      anchor=tkc.W,
                                      background=colors.JAMA_HILO_SILVER)

        # Pack the frame
        self.status_label.pack(side=tkc.LEFT, fill=tkc.X)
        self.execute_button.pack(side=tkc.RIGHT)


class StatusPanel(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg=colors.JAMA_HILO_SILVER)

        # Set reference to parent
        self.parent = master

        # Add a progress bar
        self.progress_bar = ttk.Progressbar(self, variable=self.parent.progress, mode="determinate")

        # Pack The Frame
        self.progress_bar.pack(fill=tkc.X)
