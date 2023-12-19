"""
XML Generation for VAS File Architect
Generates a completed XML file.
Image masks are grouped into WatchZones by directory and bounding box values.

Functions:
  group_images(all_image_data): Groups image masks with shared bounding box coordinates.
  enforce_unique_name(base_name, existing_names): Enforces unique WatchZone names when multiple shared WatchZones are created within the same directory.
  create_watchzone(params): Handles the creation of each individual WatchZone.
  format_xml(elem, level=0): Formats XML content to avoid the enormous single line.
  create_xml(all_image_data, root_directory): Produces 'structure.xml' content.
Parameters:
  all_image_data (list of dict): Processed imaga data, includes file path and bounding box.
  base_name (str): Base name for WatchZones, taken from current directory.
  existing_names (set): Set of existing WatchZone names.
  params (dict): Collection of all WatchZone parameters.
  elem (ET.Element): XML element to format.
  level (int, optional): Current indentation level. Defaults to 0.
  root_directory (str): Directory for XML file generation.
Returns:
  mask_names (list): Names of masks derived from images.
  xml_content (str): XML content as a string.

Note:
- Screen Geometry is hard-coded at 720p until I hear about it causing issues.
"""
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
from io import BytesIO
  
def group_images(all_image_data):
  # Dictionary for image masks with identical path and bbox values
  grouped_images = {}
  for image_data in all_image_data:
    directory = image_data['filepath'].parent
    bbox = image_data['bbox']
    key = (directory, bbox)
    if key not in grouped_images:
      grouped_images[key]= []
    grouped_images[key].append(image_data)
  return grouped_images

def enforce_unique_name(base_name, existing_names):
  # Avoid duplicate names in case of multiple groups within a directory
  if base_name not in existing_names:
    return base_name
  else:
    count = 1
    new_name = f"{base_name}_{count}"
    while new_name in existing_names:
      count += 1
      new_name = f"{base_name}_{count}"
    return new_name

def create_watchzone(params):
  # Unpack dictionary of parameters
  directory = params['directory']
  bbox = params['bbox']
  images = params['images']
  watchzones = params['watchzones']
  existing_names = params['existing_names']
  root_directory = params['root_directory']
  mask_names = params['mask_names']

  # Prevent duplicate WatchZone names
  unique_name = enforce_unique_name(directory.stem, existing_names)
  existing_names.add(unique_name)
  watchzone = ET.SubElement(watchzones, "WatchZone")
  ET.SubElement(watchzone, "Name").text = unique_name

  # Add Geometry for each WatchZone
  geometry = ET.SubElement(watchzone, "Geometry")
  ET.SubElement(geometry, "X").text = str(bbox[0])
  ET.SubElement(geometry, "Y").text = str(bbox[1])
  ET.SubElement(geometry, "Width").text = str(bbox[2] - bbox[0])
  ET.SubElement(geometry, "Height").text = str(bbox[3] - bbox[1])    

  # Add Watches and Watcher elements
  watches = ET.SubElement(watchzone, "Watches")
  watcher = ET.SubElement(watches, "Watcher")
  ET.SubElement(watcher, "Name").text = directory.stem
  watch_images = ET.SubElement(watcher, "WatchImages")
  for image_data in images:
    watch_image = ET.SubElement(watch_images, "WatchImage")
    relative_path = image_data['filepath'].relative_to(root_directory)
    ET.SubElement(watch_image, "FilePath").text = str(relative_path)
    mask_names.append(image_data['filepath'].stem)

def format_xml(elem, level=0):
  # Add newlines and indents for readability
  i = "\n" + level * "\t"
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "\t"
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      format_xml(elem, level + 1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

def create_xml(all_image_data, root_directory):
  namespaces = {'xsd': "http://www.w3.org/2001/XMLSchema", 
                'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
  # Create XML tree elements
  game_profile = ET.Element("GameProfile", attrib={f"xmlns:{k}": v for k, v in namespaces.items()})
  game_profile.insert(0, ET.Comment("Generated using VAS File Architect: https://github.com/phrayse/VAS-File-Architect"))
  ET.SubElement(game_profile, "Name").text = Path(root_directory).name
  screens = ET.SubElement(game_profile, "Screens")
  screen = ET.SubElement(screens, "Screen")
  ET.SubElement(screen, "Name").text = "Game"
  geometry = ET.SubElement(screen, "Geometry")
  ET.SubElement(geometry, "Width").text = "1280"
  ET.SubElement(geometry, "Height").text = "720"
  watchzones = ET.SubElement(screen, "WatchZones")

  # Group images for shared WatchZones
  grouped_images = group_images(all_image_data)

  # Create a WatchZone for each unique set of bounding box values
  existing_names = set()
  mask_names = []
  for (directory, bbox), images in grouped_images.items():
    watchzone_params = {
      'directory': directory,
      'bbox': bbox,
      'images': images,
      'watchzones': watchzones,
      'existing_names': existing_names,
      'root_directory': root_directory,
      'mask_names': mask_names
    }
    create_watchzone(watchzone_params)

  # Format the XML content to add lines and indentation
  format_xml(game_profile)

  # Write to BytesIO
  try:
    tree = ET.ElementTree(game_profile)
    xml_bytes = BytesIO()
    tree.write(xml_bytes, encoding="utf-8", xml_declaration=True)
    xml_content = xml_bytes.getvalue().decode("utf-8")
    return mask_names, xml_content
  except Exception as e:
    logging.error(f"Error generating XML file at {root_directory}: {e}")