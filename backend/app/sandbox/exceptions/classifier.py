class ExceptionClassifier:

    def classify(

        self,

        exception,

    ):

        if exception.retryable:

            return "retry"

        if exception.severity == "critical":

            return "abort"

        return "fail"