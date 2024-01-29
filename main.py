"""
VAS File Architect: Main Module

Coordinates the overall workflow of the VAS File Architect. This module orchestrates the
processes of image processing, XML and ASL file generation, and the creation of a VAS
archive. It includes a GUI-based directory selection and handles the application's main
execution flow.

Functions:
    main():
        The main function to orchestrate the application workflow.
    select_directory():
        Opens a GUI dialog for directory selection and returns the chosen directory.
"""
import logging
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

from asl_generation import create_asl
from image_processing import process_all_images
from vas_archive_generation import create_vas_archive
from xml_generation import create_xml

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='w')


def select_directory():
    root = Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory()
    if not directory:
        raise FileNotFoundError("No directory selected.")
    return directory


def main():
    try:
        directory = select_directory()
        path = Path(directory)

        image_filepaths = list(path.rglob('*.png'))
        all_image_data, skipped_files = process_all_images(image_filepaths)
        if not all_image_data:
            raise RuntimeError("No valid images processed.")

        mask_names, xml_content = create_xml(all_image_data, path)
        if not mask_names:
            raise RuntimeError("XML generation failed.")

        asl_content = create_asl(mask_names)
        if not asl_content:
            raise RuntimeError("ASL generation failed.")

        create_vas_archive(all_image_data, asl_content, xml_content, path)

        final_message = "VAS archive created successfully."
        if skipped_files:
            final_message += "\n\nNote: The following files were not processed:\n" + \
                            "\n".join(str(f) for f in skipped_files)
        messagebox.showinfo("VAS File Architect", final_message)
    except (FileNotFoundError, RuntimeError, Exception) as e:
        logging.error(e)
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    main()
