"""
VAS File Architect: Main Module
Entry point for the VAS File Architect tool, orchestrating the workflow from image processing to VAS archive creation.

Functions:
  main(target_directory): Executes the primary workflow.
  select_directory(): Opens GUI for user to select target directory.
Parameters:
  target_directory(str): Directory containing raw images and where the VAS archive is saved.
"""
import logging
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

from image_processing import process_image
from xml_generation import create_xml
from asl_generation import create_asl
from vas_archive_generation import create_vas_archive

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='w')

def main(target_directory):
  # Check the provided directory exists
  if not Path(target_directory).exists():
    logging.error(f"Target directory does not exist: {target_directory}")
    return

  # Process each PNG image in the directory
  path = Path(target_directory)
  all_image_data = []
  for filepath in path.rglob('*.png'):
    logging.info(f"Processing file: {filepath}")
    result = process_image(filepath)
    if not result:
      logging.warning(f"Skipping file due to processing error: {filepath}")
      continue
    bbox, cropped_img = result
    all_image_data.append({'filepath': filepath, 'bbox': bbox, 'cropped_img': cropped_img})

  if not all_image_data:
    logging.error("No valid images processed.")
    return

  # Generate XML content if images are successfully processed.
  mask_names, xml_content = create_xml(all_image_data, target_directory)
  if not mask_names:
    logging.error("XML generation failed.")
    return

  # Generate ASL content if XML content generated properly
  asl_content = create_asl(mask_names)
  if not asl_content:
    logging.error("ASL generation failed.")
    return

  # Create VAS archive with the processed data
  create_vas_archive(all_image_data, asl_content, xml_content, target_directory)

def select_directory():
  root = Tk()
  root.withdraw() # Hide the main window
  directory = filedialog.askdirectory()
  if not directory:
    messagebox.showinfo("No Selection", "No directory selected, the application will now exit.")
    return None
  return directory

if __name__ == "__main__":
  target_directory = select_directory()
  main(target_directory)