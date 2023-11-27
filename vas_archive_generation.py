"""
VAS Archive Generation for VAS File Architect
Compiles processed images and generated XML/ASL files into a VAS archive.
The VAS archive serves as a package for use with the Video Auto Split tool.

Function:
  create_vas_archive(all_image_data, asl_content, xml_content, target_directory): Creates a VAS archive.
Parameters:
  all_image_data (list of dict): Processed image data.
  asl_content (str): ASL file content.
  xml_content (str): XML file content.
  target_directory (str): Directory for saving the VAS archive.
"""
import logging
from pathlib import Path
import zipfile
from io import BytesIO

def create_vas_archive(all_image_data, asl_content, xml_content, target_directory):
  # Convert target_directory to a Path object if it's not already
  target_directory = Path(target_directory) if not isinstance(target_directory, Path) else target_directory
  zip_file_path = target_directory / f"{target_directory.name}.zip"

  with zipfile.ZipFile(zip_file_path, 'w') as zipf:
    for image_data in all_image_data:
      filepath, cropped_img = image_data['filepath'], image_data['cropped_img']
      relative_filepath = filepath.relative_to(target_directory)
      image_bytes = BytesIO()
      cropped_img.save(image_bytes, format='PNG')
      zipf.writestr(str(relative_filepath), image_bytes.getvalue())
      logging.info(f"Cropped image added to archive: {relative_filepath}")

    if asl_content:
      zipf.writestr("script.asl", asl_content)
      logging.info("script.asl created in archive.")
    if xml_content:
      zipf.writestr("structure.xml", xml_content)
      logging.info("structure.xml created in archive.")

  logging.info(f"ZIP archive created: {zip_file_path}")

  vas_file_path = target_directory / f"{target_directory.name}.vas"
  try:
    zip_file_path.rename(vas_file_path)
  except Exception as e:
    logging.error(f"Error renaming .zip archive: {e}")
  logging.info(f"VAS archive created: {vas_file_path}")