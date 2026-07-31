class SandboxFactory:

    IMAGES = {

        "python":

            "sandbox-python:latest",

        "node":

            "sandbox-node:latest",

        "java":

            "sandbox-java:latest",

        "flutter":

            "sandbox-flutter:latest",

    }

    def image(

        self,

        language,

    ):

        return self.IMAGES[language]