import time


class MetricsCollector:

    def start(self):

        return time.perf_counter()

    def finish(

        self,

        start,

    ):

        return time.perf_counter() - start