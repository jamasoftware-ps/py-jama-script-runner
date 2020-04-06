# Python standard libs
import os
import sys
import threading
import queue
import logging
import configparser

# External Library imports
import tkinter as tk
from tkinter import ttk
import tkinter.constants as tkc
from tkinter import Text
from tkinter import messagebox
from tkinter import filedialog

# Get the Jama Client library
from py_jama_rest_client.client import JamaClient

# Local imports:
import custom_widgets as cw

# Constant / lookup value imports
import colors
import app_constants as const

# Custom Widget types
STRING_FIELD_WIDGET = "STRING_FIELD_WIDGET"
RADIO_BUTTON_FIELD_WIDGET = "RADIO_BUTTON_FIELD_WIDGET"
DIRECTORY_CHOOSER_FIELD_WIDGET = "DIRECTORY_CHOOSER_FIELD_WIDGET"


########################################################################################################################
# GUI Components
########################################################################################################################
class PyJamaScriptRunner(tk.Tk):
    logger = logging.getLogger("Application")

    def __init__(self, custom_widgets, func_to_run):
        """
        :param custom_widgets: This is a dict of desired custom widgets, each Key Value pair will be passed as kwargs to
            the run function later
        :param func_to_run: This should be a function that takes **kwargs as its only parameter.  then the keys from the
            custom widgets dict will be passed to this function with the corresponding gathered values.
        """
        # Initialize Tk application
        tk.Tk.__init__(self)

        # Internal variables
        self.target = func_to_run
        self.script_running = False
        self.message_queue = queue.Queue()
        self.work_thread = None
        self.progress = tk.DoubleVar()
        self.status = tk.StringVar(value="Ready")
        self.custom_fields = {}

        # Set the title of the application
        self.title(const.TITLE)

        # Set the window size
        self.geometry(const.RESOLUTION)

        # Set Background Color
        self.configure(background=colors.JAMA_HILO_SILVER)

        # Build a Menu bar
        self.menubar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Load settings", command=self.load_settings)
        self.file_menu.add_command(label="Save settings", command=self.save_settings)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.config(menu=self.menubar)

        # Setup client connection settings frame
        self.client_panel = ClientSettingsPanel(self)

        # Setup Script Input Section
        self.script_settings_panel = ScriptSettingsPanel(self, custom_widgets, self.custom_fields)

        # Setup Script Output Section
        self.results_panel = ResultsPanel(self)

        # Setup Execute Button
        self.execute_panel = ExecutePanel(self)

        # Setup Status / Progress bar
        self.status_frame = StatusPanel(self)

        # Pack the application.
        self.client_panel.pack(fill=tkc.X)
        self.script_settings_panel.pack(fill=tkc.X)
        self.results_panel.pack(fill=tkc.BOTH, expand=1)
        self.status_frame.pack(side=tkc.BOTTOM, fill=tkc.X)
        self.execute_panel.pack(side=tkc.BOTTOM, fill=tkc.X)

        # attempt to load existing settings.iml file
        self.default_settings_file = 'settings.ini'

        # determine if application is a script file or frozen exe
        self.application_path = ""
        if getattr(sys, 'frozen', False):
            self.application_path = '/'.join(os.path.dirname(sys.argv[0]).split('/')[:-3])
        elif __file__:
            self.application_path = '/'.join(os.path.dirname(__file__).split('/')[:-1])

        config_path = os.path.join(self.application_path, self.default_settings_file)
        self.load_file(config_path)

    def save_settings(self):
        save_location = filedialog.asksaveasfilename(initialdir=self.application_path,
                                                     initialfile=self.default_settings_file,
                                                     title="Select save file",
                                                     filetypes=(("Config files", "*.ini"), ("all files", "*")),
                                                     defaultextension=".ini")

        config = configparser.ConfigParser()
        config['CLIENT'] = {
            'jama_url': self.client_panel.url_field.get_value(),
            'oauth': str(self.client_panel.auth_mode_field.auth_mode.get()),
            'user_id': self.client_panel.username_field.get_value(),
            # Uncomment the following line to allow the saving of password fields
            # 'secret': self.client_panel.password_field.get_value()
        }
        config['CUSTOM_FIELDS'] = {}
        for field in self.custom_fields.keys():
            config['CUSTOM_FIELDS'][field] = str(self.custom_fields.get(field).get_value())

        with open(save_location, 'w') as config_file:
            config.write(config_file)

    def load_settings(self):
        file_to_load = filedialog.askopenfilename(initialdir=self.application_path,
                                                  initialfile=self.default_settings_file,
                                                  title="Select save file",
                                                  filetypes=(("Config files", "*.ini"), ("all files", "*")),
                                                  defaultextension=".ini")
        if file_to_load != '':
            self.load_file(file_to_load)

    def load_file(self, file_to_load):
        config = configparser.ConfigParser()
        config.read(file_to_load)

        # Load client settings
        self.client_panel.url_field.set_value(config.get("CLIENT", "jama_url"))
        self.client_panel.auth_mode_field.auth_mode.set(int(config.get("CLIENT", "oauth")))
        self.client_panel.username_field.set_value(config.get("CLIENT", "user_id"))
        try:
            self.client_panel.password_field.set_value(config.get("CLIENT", "secret"))
        except configparser.NoOptionError:
            pass

        # Load custom settings
        for option in config.options("CUSTOM_FIELDS"):
            if option in self.custom_fields:
                self.custom_fields.get(option).set_value(config.get("CUSTOM_FIELDS", option))

    def execute_button_command(self):
        """This function should start a thread to do the work of the custom script. The script can pass back messages
        via a message queue."""
        # If the script is already started, we dont want to start it twice.
        self.execute_panel.execute_button.config(state=tkc.DISABLED)

        # Before we proceed lets set the status of this to script to running before another button click can happen.
        self.script_running = True

        # Create a Message Queue for the background thread to communicate to us on.
        self.message_queue = queue.Queue()

        # Clear out Results page:
        self.results_panel.clear()

        # Parse arguments
        try:
            kwargs = self.get_form_params()

        except Exception as e:
            # If error during parameter parsing and validation, then reset running vars and button state to normal
            self.logger.error(e)
            self.script_running = False
            self.execute_panel.execute_button.configure(state=tkc.NORMAL)
            return

        # Start messaging queue reader
        self.after(100, func=self.__periodic_message_queue_handler)

        # Create New Thread and start our script functionality in it.
        self.work_thread = threading.Thread(
            target=self.target,
            kwargs=kwargs,  # A Dictionary of named arguments for the target function
            daemon=True
        )
        self.work_thread.start()

        # Begin periodic thread completion check.
        self.after(300, func=self.__periodic_check_work_thread_completed)

    def __periodic_message_queue_handler(self):
        """
        This method will periodically check the message queue and add any queued messages to the Results Panel.
        :return:
        """
        # Get all messages out of the queue.
        while not self.message_queue.empty():
            try:
                self.results_panel.append_message(self.message_queue.get())
            except queue.Empty:
                pass

        # As long as the script is still running we must keep re-scheduling this task.
        if self.script_running:
            self.after(40, func=self.__periodic_message_queue_handler)

    def __periodic_check_work_thread_completed(self):
        """
        This function periodically checks to see if our background job is done, when it is. we will re-enable the GUI
        for another execution.
        :return:
        """
        if self.work_thread.is_alive():
            # If the thread is still active, do nothing right now. and reschedule this method
            self.after(500, func=self.__periodic_check_work_thread_completed)
        else:
            # Set running status to false to signal the end of the Message queue manager
            self.script_running = False
            # Set the Execute button to normal state so that it can be used again.
            self.execute_panel.execute_button.config(state=tkc.NORMAL)

    def get_form_params(self):
        kwargs = {
            "client": self.client_panel.get_client()
        }

        for custom_field in self.custom_fields.keys():
            kwargs[custom_field] = self.custom_fields.get(custom_field).get_value()

        return kwargs

    def emit_message(self, msg):
        self.message_queue.put(msg)

    def set_status_message(self, msg):
        self.status.set(msg)
        self.message_queue.put("\n")

    def update_progress(self, progress):
        """
        Update the progress bar
        :param progress: The int value of the current progress of this task
        :return: none
        """
        self.progress.set(progress)


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


class ScriptSettingsPanel(tk.LabelFrame):
    """
    This class defines the custom settings panel for the custom script.  Any special parameters needed by the custom
    script shall be defined and collected here.
    """

    def __init__(self, master, custom_widgets, custom_fields):
        tk.LabelFrame.__init__(self, master, text=const.SCRIPT_SETTINGS_PANEL_LABEL, bg=colors.JAMA_HILO_SILVER)

        # Set back reference
        self.parent = master

        # Add custom fields here
        for field in custom_widgets.keys():
            try:
                field_config = custom_widgets.get(field)
                field_widget = None
                field_label = field_config.get('label')
                field_type = field_config.get('type')
                if field_type == STRING_FIELD_WIDGET:
                    field_widget = cw.StringFieldWidget(self, field_label)
                elif field_type == DIRECTORY_CHOOSER_FIELD_WIDGET:
                    field_widget = cw.DirectoryChooserFieldWidget(self, field_label)
                elif field_type == RADIO_BUTTON_FIELD_WIDGET:
                    options = field_config.get('options')
                    radio_button_widget = cw.RadioButtonFieldWidget(self, field_label, options)
                    field_widget = radio_button_widget
                field_widget.pack(fill=tkc.X)
                custom_fields[field] = field_widget
            except Exception as e:
                print(e)
                pass


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
        self.url_field = cw.StringFieldWidget(self, const.URL_LABEL)

        # Prompt for Auth Mode
        self.auth_mode_field = AuthModeSelector(self)

        # Create Username Field
        self.username_field = cw.StringFieldWidget(self, const.USERNAME)
        self.password_field = cw.StringFieldWidget(self, const.PASSWORD, show='*')

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
            url = self.url_field.value.get().strip().lower()
            # Get those pesky backslashes out
            while url.endswith('/'):
                url = url[0:len(url) - 1]
            # If http or https method not specified in the url then add it now.
            if not (url.startswith('https://') or url.startswith('http://')):
                url = 'https://' + url
            self.url_field.value.set(url)

            if self.auth_mode_field.auth_mode.get() == AuthModeSelector.AUTH_MODE_BASIC:
                use_oauth = False
            else:
                use_oauth = True
            username = self.username_field.value.get().strip()
            password = self.password_field.value.get().strip()
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
