# Py Jama Script Runner
This library provides a basic framework for python GUI applications.  It is intended to allow for the rapid development
and deployment of custom python scripts, while giving the user a more finished experience than a command line
application.

### Features
* Client Management: Settings related to Jama REST API connection are handled.
* Custom Field Management: Define the fields you need.  The GUI will automatically create fields to collect user input.
* Logging: Logs will automatically be output to a logs/ directory next to the application.
* Packaging: You can package your application as a MacOS app or Windows executable.


## How to use this library

The file "print_projects.py" Can be referenced as an example of how to use project.

1) **Define** the input parameters for your script that the user will enter through the GUI.

    #### Custom Widgets:
    You can choose from the following type of Input widget for your fields.
    * String Field Widget
    * Radio Button Widget
    * Directory Chooser Widget
    * additional widget types to be added in the future such as File chooser, ComboBox, and other common form elements.
    
    This is an example custom widget dictionary declaration:
    ```python
    custom_widgets = {
        "project_id": {
            "type": py_jama_script_runner.STRING_FIELD_WIDGET,  # Always declare your desired widget "type"
            "label": "Project ID:"                              # Here you can define your widgets Label text
        },
        "mapping_version": {
            "type": py_jama_script_runner.RADIO_BUTTON_FIELD_WIDGET,
            "label": "Mapping Version:",
            "options": ["A", "B", "C", "D"]  # you will be returned the index of the option the user chooses from this list
        },
        "output_location": {
            "type": py_jama_script_runner.DIRECTORY_CHOOSER_FIELD_WIDGET,
            "label": "Output Directory:"
        }
    }
    ```
    #### Note:
    REST Client parameters are handled for you.  You only need to define the parameters required for your scripts 
    business logic.
    
2) Create a run function.  this is the function that will be called when the "Execute" button is clicked by the user.
  This function should only have keyword arguments and not rely positional arguments.

3) Creating an instance of the PyJamaScriptRunner class. You must supply two parameters to the constructor. \
  The first is the dictionary object from Step 1 above that describes which custom widgets should be applied to the custom 
  script settings section of the GUI.  The second is the run function created in Step 2 above.

4) Call the mainloop function of the PyJamaScriptRunner class instantiated in Step 3 above to launch the GUI.  Note that
this method does not return until the user closes the application.  you must do any setup required before calling 
this method.

### How to interact with the GUI from your script.
There are 3 ways to update and interact with the GUI:

*  Status Field: <br> The status field allows you to inform the user what the application is currently doing.  The status 
field is located just above the progress bar and to the far left of the execution button.
You can use the function `set_status_message(msg)` to set the status field to the supplied msg string.  
It is suggested to updated this when the application is entering a new phase. Please keep your status field messages 
short(less than 50 characters is recommended.)

* Results Panel: <br>The results panel is where you can display bulk information to the user.  To add a message to the 
results panel you can call the `emit_message(msg)` function.  All messages passed to the results panel are also logged
to the file logger.

* Progress bar: <br>
You can inform the user of progress made by your script by updating the progress bar.
Call the `update_progress(progress)` function.  You must supply an integer between 0 - 100 inclusive.


### Packaging
You can package this application as a standalone MacOS .app package or Windows executable.  You must package Mac Apps 
on MacOS and Windows executables on a Windows machine.

#### MacOS 
1) Open a terminal to the root of the project and type `pipenv shell`
2) Enter the command `pyinstaller --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --windowed  print_projects.py app/custom_widgets.py app/colors.py app/app_constants.py app/py_jama_script_runner.py`
Note: you may have to edit the path to your tk and tcl libraries if located at another path.

#### Windows
1) Open a terminal to the root of the project and type `pipenv shell`
2) Enter the command `pyinstaller  --windowed  print_projects.py app/custom_widgets.py app/colors.py app/app_constants.py app/py_jama_script_runner.py`