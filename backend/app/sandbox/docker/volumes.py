# Volumes module
class VolumeManager:

    def workspace(

        self,

        path,

    ):

        return {

            path: {

                "bind": "/workspace",

                "mode": "rw",

            }

        }