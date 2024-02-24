"""
VAS File Architect

Coordinates the overall workflow:
 - image processing,
 - ASL and XML file generation,
 - creation of a VAS archive.

Creates a log file in the target directory.

Acts as the error handler for all other modules.
"""
import logging
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

from asl_generation import create_asl
from image_processing import process_all_images
from vas_archive_generation import create_vas_archive
from xml_generation import create_xml

logging.getLogger("PIL").setLevel(logging.INFO)


def select_directory():
    """
    Open an interface for directory selection.

    :return: Path to chosen directory.
    :rtype: Path
    :raise FileNotFoundError: if no directory was selected, or selected directory does not exist.
    """
    root = Tk()
    root.withdraw()
    directory = Path(filedialog.askdirectory(mustexist=True))

    if not directory:
        raise FileNotFoundError("No directory selected.")

    log_file = directory / 'vasfa.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s:%(filename)s: %(lineno)d - %(message)s',
                        filename=log_file,
                        filemode='w')

    return directory


def main():
    """
    Orchestrates the workflow of image processing, XML and ASL file generation, and VAS archive creation.

    :rtype: None
    :raise RuntimeError: if any of the key processes fail: image processing, XML generation,
    ASL generation, or VAS archive generation.
    """
    try:
        path = select_directory()

        logging.info("Gathering .png files.")
        image_filepaths = list(path.rglob('*.png'))

        all_image_data, skipped_files = process_all_images(image_filepaths)

        if not all_image_data:
            raise RuntimeError("No valid images processed.")

        logging.info("Image files processed. Generating XML.")
        mask_names, xml_content = create_xml(all_image_data, path)

        if not mask_names:
            raise RuntimeError("XML generation failed.")

        logging.info("Completed XML. Generating ASL.")
        asl_content = create_asl(mask_names)

        if not asl_content:
            raise RuntimeError("ASL generation failed.")

        logging.info("Completed ASL. Generating VAS archive.")
        create_vas_archive(all_image_data, asl_content, xml_content, path)

        final_message = "VAS archive created successfully."

        if skipped_files:
            final_message += "\n\nNote: The following files were not processed:\n" + \
                            "\n".join(str(f) for f in skipped_files)

        logging.info(final_message)
        messagebox.showinfo("VAS File Architect", final_message)
    except FileNotFoundError as e:
        logging.error(e)
    except (RuntimeError, Exception) as e:
        logging.error(e)
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    main()
