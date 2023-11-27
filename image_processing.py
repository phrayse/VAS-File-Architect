"""
Image Processing for VAS File Architect
Handles the cropping of non-transparent areas in mask images.

Functions:
  process_image(filepath): Identifies and crops non-transparent areas.
Parameters:
  filepath (str): Path to the image file.
Returns:
  bbox, cropped_img: Bounding box and cropped image file.
"""
import logging
from PIL import Image

def process_image(filepath):
  try:
    with Image.open(filepath) as img:
      if img.mode != 'RGBA':
        logging.info(f"Converting {filepath} to RGBA")
        img = img.convert('RGBA')
      bbox = img.getbbox()
      logging.debug(bbox)

      if bbox:
        cropped_img = img.crop(bbox)
        logging.info(f'Image processed: {filepath}')
        return bbox, cropped_img
      else:
        logging.warning(f'No non-transparent area found in {filepath}')
  except IOError as e:
    logging.error(f'IOError while accessing {filepath}: {e}')
  except Exception as e:
    logging.error(f'Unexpected error while processing file {filepath}: {e}')