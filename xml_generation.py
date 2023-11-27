"""
XML Generation for VAS File Architect
Generates XML content for WatchZones based on processed image data.

Functions:
  format_xml(elem, level=0): Formats XML content to avoid the enormous single line.
  create_xml(all_image_data, root_directory): Produces 'structure.xml' content.
Parameters:
  elem (ET.Element): XML element to format.
  level (int, optional): Current indentation level. Defaults to 0
  all_image_data (list of dict): Processed imaga data.
  root_directory (str): Directory for conceptual XML generation.
Returns:
  mask_names (list): A list of mask names derived from the processed images, to be used in ASL file generation.
  xml_content (str): Content of the XML file to be created.

Note:
- Screen Geometry is hard-coded at 720p until I hear about it causing issues.
"""
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
from io import BytesIO

def format_xml(elem, level=0):
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
  game_profile.insert(0, ET.Comment("Generated using VAS File Architect by Phrayse (fast@phrayse.au)"))
  game_profile.insert(1, ET.Comment("https://github.com/phrayse/VAS-File-Architect"))
  ET.SubElement(game_profile, "Name").text = Path(root_directory).name
  screens = ET.SubElement(game_profile, "Screens")
  screen = ET.SubElement(screens, "Screen")
  ET.SubElement(screen, "Name").text = "Game"
  geometry = ET.SubElement(screen, "Geometry")
  ET.SubElement(geometry, "Width").text = "1280"
  ET.SubElement(geometry, "Height").text = "720"
  watchzones = ET.SubElement(screen, "WatchZones")

  # Process each image's data
  mask_names = []
  for image_data in all_image_data:
    bbox = image_data['bbox']
    filepath = image_data['filepath']
    watchzone = ET.SubElement(watchzones, "WatchZone")
    ET.SubElement(watchzone, "Name").text = filepath.stem

    # Add Geometry for each WatchZone
    geometry = ET.SubElement(watchzone, "Geometry")
    ET.SubElement(geometry, "X").text = str(bbox[0])
    ET.SubElement(geometry, "Y").text = str(bbox[1])
    ET.SubElement(geometry, "Width").text = str(bbox[2] - bbox[0])
    ET.SubElement(geometry, "Height").text = str(bbox[3] - bbox[1])

    # Add Watches and Watcher elements
    watches = ET.SubElement(watchzone, "Watches")
    watcher = ET.SubElement(watches, "Watcher")
    ET.SubElement(watcher, "Name").text = filepath.stem

    # Add WatchImages and WatchImage elements
    watch_images = ET.SubElement(watcher, "WatchImages")
    watch_image = ET.SubElement(watch_images, "WatchImage")
    relative_path = filepath.relative_to(root_directory)
    ET.SubElement(watch_image, "FilePath").text = str(relative_path)

    # Add mask to list for .asl file
    mask_names.append(filepath.stem)

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