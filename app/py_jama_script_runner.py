# External Library imports
import tkinter as tk
import tkinter.constants as tkc

import threading
import queue
import logging
from PIL import Image, ImageTk

# Local imports:
import custom_widgets as cw

# Constant / lookup value imports
import colors
import app_constants as const


########################################################################################################################
# GUI Components
########################################################################################################################
class Application(tk.Tk):
    logger = logging.getLogger("Application")

    def __init__(self):
        # Initialize Tk application
        tk.Tk.__init__(self)

        # Internal variables
        self.target = None
        self.script_running = False
        self.message_queue = None
        self.work_thread = None
        self.progress = tk.DoubleVar()
        self.status = tk.StringVar(value="Ready")

        # Set the title of the application
        self.title(const.TITLE)

        # Set the window size
        self.geometry(const.RESOLUTION)

        # Set Background Color
        self.configure(background=colors.JAMA_HILO_SILVER)

        # Set Logo - Attempt to load and move on if failure
        try:
            logo = Image.open("logo.png").resize((263, 70))
            rendered_logo = ImageTk.PhotoImage(logo)
            self.logo_label = tk.Label(self, image=rendered_logo, bg=colors.JAMA_HILO_SILVER)
            self.logo_label.image = rendered_logo
            self.logo_label.pack(fill=tkc.X)
        except FileNotFoundError:
            pass

        # Setup client connection settings frame
        self.client_panel = cw.ClientSettingsPanel(self)

        # Setup Script Input Section
        self.script_settings_panel = cw.ScriptSettingsPanel(self)

        # Setup Script Output Section
        self.results_panel = cw.ResultsPanel(self)

        # Setup Execute Button
        self.execute_panel = cw.ExecutePanel(self)

        # Setup Status / Progress bar
        self.status_frame = cw.StatusPanel(self)

        # Pack the application.
        self.client_panel.pack(fill=tkc.X)
        self.script_settings_panel.pack(fill=tkc.X)
        self.results_panel.pack(fill=tkc.BOTH, expand=1)
        self.status_frame.pack(side=tkc.BOTTOM, fill=tkc.X)
        self.execute_panel.pack(side=tkc.BOTTOM, fill=tkc.X)

    def run(self, **kwargs):
        """This function is to be overloaded, and business logic shall be inserted here."""
        print("Default run method should be overloaded.")

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
            target=self.run,
            kwargs=kwargs,  # A Dictionary of named arguments for the target function
            daemon=True
        )
        self.work_thread.start()

        # Begin periodic thread completion check.
        self.after(500, func=self.__periodic_check_work_thread_completed)

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
        return kwargs


if __name__ == "__main__":
    app = Application()
    app.mainloop()
