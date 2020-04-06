# Py Jama Script Runner
This library provides a basic framework for python GUI applications.  It is intended to allow for the rapid development
and deployment of custom python scripts, while giving the user a more finished experience than a command line
application.


## How to use this library

The file "print_projects.py" Can be referenced as an example project.

1) **Define** the input parameters for your script that the user will enter through the GUI.    To def

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
            "options": ["A", "B", "C", "D"]
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
    
2)

Begin by creating an instance of the PyJamaScriptRunner class. You must supply two parameters, the first is a 
    dictionary object that describes which custom widgets should be applied to the custom script settings section of the
    GUI.  The second is a function that will be executed when the execute button is clicked.  

2) Your Run method supplied to the constructor should have no positional arguments and should accept a list of kwargs.
    The kwargs dictionary passed to your supplied function will contain an value for each of the defined custom widgets
    that you defined during instantiation.



so that you will have access to update the GUI, i.e. Message output, Status field and 
progress bar.  

    You will have access to three methods that update/interact wtih the GUI.
    * `set_status_message(msg)` Sets the status field to the supplied string.  It is suggested to updated this one the
    application is entring a new phase
 



WIP: SORRY WE ARE STILL UNDER CONSTRUCTION....