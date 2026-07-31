class NetworkMonitor:

    def __init__(self):

        self.requests = []

    def attach(self, page):

        page.on(

            "request",

            lambda req: self.requests.append(

                req.url

            ),

        )