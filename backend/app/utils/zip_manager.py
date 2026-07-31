from pathlib import Path
import zipfile
import shutil

from pathlib import Path
import zipfile


class ZipManager:

    ...

    @staticmethod
    def extract(zip_path: Path, destination: Path):

        destination = destination.resolve()

        with zipfile.ZipFile(zip_path) as zip_ref:

            for member in zip_ref.infolist():

                extracted_path = (
                    destination / member.filename
                ).resolve()

                if not str(extracted_path).startswith(
                    str(destination)
                ):
                    raise Exception(
                        "Unsafe ZIP detected."
                    )

                zip_ref.extract(
                    member,
                    destination,
                )


    @staticmethod
    def validate_zip(zip_path: Path):

        if not zip_path.exists():
            raise FileNotFoundError("ZIP file not found.")

        if zip_path.stat().st_size > ZipManager.MAX_SIZE:
            raise ValueError("ZIP exceeds maximum size.")

        if zip_path.suffix.lower() != ".zip":
            raise ValueError("Only ZIP files are allowed.")

   
    @staticmethod
    def delete(zip_path: Path):

        if zip_path.exists():
            zip_path.unlink()