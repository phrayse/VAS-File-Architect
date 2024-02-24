"""
VAS Archive Generation for VAS File Architect

Compiles processed images, `script.asl`, and `structure.xml` into a VAS archive.
"""
import logging
import zipfile
from io import BytesIO
from pathlib import Path


def create_vas_archive(all_image_data, asl_content, xml_content, target_directory):
    """
    Creates and saves the VAS archive.

    :param list of dict all_image_data: Processed image data.
    :param str asl_content: Contents of `script.asl`.
    :param str xml_content: Contents of `structure.xml`.
    :param Path target_directory: Target directory into which the VAS archive will be written.
    :rtype: None
    :raise RuntimeError:
    """
    vas_file_path = target_directory / f"{target_directory.name}.vas"

    try:
        with zipfile.ZipFile(vas_file_path, 'w') as zipf:
            for image_data in all_image_data:
                filepath, cropped_img = image_data['filepath'], image_data['cropped_img']
                relative_filepath = filepath.relative_to(target_directory)
                image_bytes = BytesIO()
                cropped_img.save(image_bytes, format='PNG')
                zipf.writestr(str(relative_filepath), image_bytes.getvalue())
                logging.info(f"Cropped image added to archive: {relative_filepath}")

            zipf.writestr("script.asl", asl_content)
            logging.info("script.asl created in archive.")

            zipf.writestr("structure.xml", xml_content)
            logging.info("structure.xml created in archive.")

        logging.info(f"VAS archive created: {vas_file_path}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error in creating VAS archive at {vas_file_path}: {e}")
