import time

import py_jama_script_runner


class CustomizedApp(py_jama_script_runner.Application):
    def __init__(self):
        py_jama_script_runner.Application.__init__(self)

    def run(self, **kwargs):
        """
        The Entry point for this applications business logic.
        :param kwargs: A dict that must contains all needed parameters URL, Username and Password
        :return: None
        """
        self.get_projects(
            kwargs.get("client")
        )

    def get_projects(self, client):
        # Create the JamaClient
        jama_client = client

        # Get the list of projects from Jama
        # The client will return to us a JSON array of Projects, where each project is a JSON object.
        project_list = jama_client.get_projects()

        # Print the data out for each project.
        for index, project in enumerate(project_list):
            self.status.set("Running: " + str(index) + "/" + str(len(project_list)))
            self.progress.set(int(index/len(project_list) * 100))
            project_name = project['fields']['name']
            self.message_queue.put('\n---------------' + project_name + '---------------')

            # Print each field
            for field_name, field_data in project.items():

                # If one of the fields(i.e. "fields") is a dictionary then print it's sub fields indented.
                if isinstance(field_data, dict):
                    self.message_queue.put(str(field_name))
                    self.message_queue.put(':')
                    # Print each sub field
                    for sub_field_name in field_data:
                        sub_field_data = field_data[sub_field_name]
                        self.message_queue.put('\t' + str(sub_field_name) + ': ' + str(sub_field_data))

                # If this field is not a dictionary just print its field.
                else:
                    self.message_queue.put(str(field_name) + ': ' + str(field_data))
            self.message_queue.put('\n')

            time.sleep(0.005)
        self.progress.set(100)
        self.status.set("Ready")

if __name__ == "__main__":
    app = CustomizedApp()
    app.mainloop()
