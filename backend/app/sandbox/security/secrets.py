import re


class SecretRedactor:

    PATTERNS = [

        re.compile(r"sk-[A-Za-z0-9_-]+"),

        re.compile(r"AKIA[0-9A-Z]{16}"),

    ]

    def redact(

        self,

        text: str,

    ) -> str:

        for pattern in self.PATTERNS:

            text = pattern.sub(

                "***REDACTED***",

                text,

            )

        return text