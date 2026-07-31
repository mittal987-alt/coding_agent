from pathlib import Path

from app.testing.models import TestSuite


class TestDetector:

    def detect(
        self,
        workspace: Path,
    ) -> TestSuite:

        if (workspace / "pytest.ini").exists():

            return TestSuite.PYTEST

        if (workspace / "package.json").exists():

            return TestSuite.JEST

        if (workspace / "pubspec.yaml").exists():

            return TestSuite.FLUTTER

        return TestSuite.UNKNOWN