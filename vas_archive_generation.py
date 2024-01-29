"""
VAS Archive Generation for VAS File Architect

Compiles processed images, along with generated XML and ASL files, into a VAS archive.
This module facilitates the packaging of these components into a single VAS file, which
is then used with the Video Auto Split tool.

Functions:
    create_vas_archive(all_image_data, asl_content, xml_content, target_directory):
        Creates and saves the VAS archive.
        Arg:
            all_image_data (list of dict): Processed image data.
            asl_content (str): Content of the ASL file.
            xml_content (str): Content of the XML file.
            target_directory (Path): Target directory to save the VAS archive.
"""
import logging
import zipfile
from io import BytesIO


def create_vas_archive(all_image_data, asl_content, xml_content, target_directory):
    vas_file_path = target_directory / f"{target_directory.name}.vas"
    logging.info("Beginning VAS archive creation.")
    try:
        with zipfile.ZipFile(vas_file_path, 'w') as zipf:
            for image_data in all_image_data:
                try:
                    filepath, cropped_img = image_data['filepath'], image_data['cropped_img']
                    relative_filepath = filepath.relative_to(target_directory)
                    image_bytes = BytesIO()
                    cropped_img.save(image_bytes, format='PNG')
                    zipf.writestr(str(relative_filepath), image_bytes.getvalue())
                    logging.info(f"Cropped image added to archive: {relative_filepath}")
                except Exception as e:
                    raise RuntimeError(f"Error processing image {filepath}: {e}")

            logging.info("Beginning ASL and XML file creation.")
            zipf.writestr("script.asl", asl_content)
            logging.info("script.asl created in archive.")
            zipf.writestr("structure.xml", xml_content)
            logging.info("structure.xml created in archive.")

        logging.info(f"VAS archive created: {vas_file_path}")
    except zipfile.BadZipfile as e:
        raise RuntimeError(f"BadZipFile error in creating VAS archive at {vas_file_path}: {e}")
    except IOError as e:
        raise RuntimeError(f"IOError in creating VAS archive at {vas_file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error in creating VAS archive at {vas_file_path}: {e}")
