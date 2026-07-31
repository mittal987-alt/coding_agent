# Images module
class ImageManager:

    def __init__(

        self,

        client,

    ):

        self.client = client

    def ensure(

        self,

        image,

    ):

        try:

            self.client.images.get(image)

        except Exception:

            self.client.images.pull(image)