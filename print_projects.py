import time

import app.py_jama_script_runner as pjsr

# The list of custom widgets we want for our customized script runner app
custom_widgets = {
    "project_id": {
        "type": pjsr.STRING_FIELD_WIDGET,
        "label": "Project ID:"
    },
    "mapping_version": {
        "type": pjsr.RADIO_BUTTON_FIELD_WIDGET,
        "label": "Mapping Version:",
        "options": ["A", "B", "C", "D"]
    },
    "item_type": {
        "type": pjsr.COMBOBOX_FIELD_WIDGET,
        "label": "Item Type:",
        "options": ["Component", "Folder", "Text", "Item"]
    },
    "input_file": {
        "type": pjsr.FILE_CHOOSER_FIELD_WIDGET,
        "label": "Input File:"
    },
    "output_location": {
        "type": pjsr.DIRECTORY_CHOOSER_FIELD_WIDGET,
        "label": "Output Directory:"
    }
}


class CustomizedApp:
    def __init__(self):
        # Setup the GUI with the needed widgets and run method.
        self.app = pjsr.PyJamaScriptRunner(custom_widgets, self.run)
        # Start the GUI:
        self.app.mainloop()
        # NO MORE CODE BELOW HERE:  mainloop will not return until after the program exits.

    def run(self, **kwargs):
        """
        The Entry point for this applications business logic.
        :param kwargs: A dict that must contains all needed parameters i.e. client
        :return: None
        """
        # Display the client configured by the user.
        self.app.emit_message("Input Parameters:")
        client = None
        try:
            client = kwargs.get('client')
            self.app.emit_message("Client: " + str(client))
        except KeyError:
            self.app.emit_message("Unable to locate client argument.")

        # Display the data in custom fields to the user.
        for custom_field_name in custom_widgets.keys():
            try:
                field_data = kwargs.get(custom_field_name)
                self.app.emit_message('{}: {}'.format(custom_field_name, str(field_data)))
            except KeyError:
                self.app.emit_message("Unable to locate argument {}.".format(custom_field_name))

        if client is not None:
            self.get_projects(client)

    def get_projects(self, client):
        # Create the JamaClient
        jama_client = client

        # Get the list of projects from Jama
        # The client will return to us a JSON array of Projects, where each project is a JSON object.
        project_list = jama_client.get_projects()

        # Print the data out for each project.
        for index, project in enumerate(project_list):
            self.app.set_status_message("Running: " + str(index) + "/" + str(len(project_list)))
            self.app.update_progress(int(index/len(project_list) * 100))
            project_name = project['fields']['name']
            self.app.emit_message('\n---------------' + project_name + '---------------')

            # Print each field
            for field_name, field_data in project.items():

                # If one of the fields(i.e. "fields") is a dictionary then print it's sub fields indented.
                if isinstance(field_data, dict):
                    self.app.emit_message(str(field_name))
                    self.app.emit_message(':')
                    # Print each sub field
                    for sub_field_name in field_data:
                        sub_field_data = field_data[sub_field_name]
                        self.app.emit_message('\t' + str(sub_field_name) + ': ' + str(sub_field_data))

                # If this field is not a dictionary just print its field.
                else:
                    self.app.emit_message(str(field_name) + ': ' + str(field_data))
            self.app.emit_message('\n')

            time.sleep(0.005)
        self.app.update_progress(100)
        self.app.set_status_message("Ready")


if __name__ == "__main__":
    app = CustomizedApp()
