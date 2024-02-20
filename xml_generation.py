"""
XML Generation for VAS File Architect

Responsible for generating an XML file by grouping image masks into WatchZones based on
shared bounding box coordinates. This module assists in creating unique WatchZone names,
formats the XML for readability, and maintains the structure for VAS file usage.

Functions:
    group_images(all_image_data):
        Groups image masks by shared bounding boxes.
        Arg:
            all_image_data (list of dict): Data of images with file paths and bounding boxes.
        Returns:
            defaultdict: Grouped image data by shared bounding boxes.

    enforce_unique_name(base_name, existing_names):
        Ensures unique WatchZone names.
        Arg:
            base_name (str): The base name for the WatchZone.
            existing_names (set of str): Set of existing WatchZone names to avoid duplicates.
        Returns:
            str: A unique name for the WatchZone.

    create_watchzone(params):
        Creates individual WatchZone XML elements.
        Arg:
            params (dict): Parameters for creating a WatchZone.
        Returns:
            None

    format_xml(elem, level=0):
        Formats XML elements for readability.
        Arg:
            elem (Element): The XML element to be formatted.
            level (int): Current indentation level, defaults to 0.
        Returns:
            None

    create_xml(all_image_data, root_directory):
        Generates the complete structure.xml content.
        Arg:
            all_image_data (list of dict): Data of images with file paths and bounding boxes.
            root_directory (Path): Directory for XML file generation.
        Returns:
            tuple: Contains a list of mask names and the XML content.

Note:
- Screen Geometry is hard-coded at 720p until I hear about it causing issues.
"""
import logging
import xml.etree.ElementTree as Et
from collections import defaultdict
from io import BytesIO


def group_images(all_image_data):
    logging.info("Beginning image grouping.")
    grouped_images = defaultdict(list)

    for image_data in all_image_data:
        directory = image_data['filepath'].parent
        bbox = image_data['bbox']
        key = (directory, bbox)
        grouped_images[key].append(image_data)
        logging.info(f"Appending {image_data['filepath'].stem} to group: {directory.name}_{bbox}")

    logging.info(f"Grouped {len(grouped_images)} sets of images.")
    return grouped_images


def enforce_unique_name(base_name, existing_names):
    if base_name not in existing_names:
        return base_name
    count = 1
    new_name = f"{base_name}_{count}"

    while new_name in existing_names:
        count += 1
        new_name = f"{base_name}_{count}"

    return new_name


def create_watchzone(params):
    directory = params['directory']
    bbox = params['bbox']
    images = params['images']
    watchzones = params['watchzones']
    existing_names = params['existing_names']
    root_directory = params['root_directory']
    mask_names = params['mask_names']

    unique_name = enforce_unique_name(directory.stem, existing_names)
    existing_names.add(unique_name)
    logging.info(f"Creating WatchZone: {unique_name}")

    watchzone = Et.SubElement(watchzones, "WatchZone")
    Et.SubElement(watchzone, "Name").text = unique_name

    watchzone.append(Et.Comment('ErrorMetric></ErrorMetric'))
    watchzone.append(Et.Comment('Equalize>false</Equalize'))

    geometry = Et.SubElement(watchzone, "Geometry")
    Et.SubElement(geometry, "X").text = str(bbox[0])
    Et.SubElement(geometry, "Y").text = str(bbox[1])
    Et.SubElement(geometry, "Width").text = str(bbox[2] - bbox[0])
    Et.SubElement(geometry, "Height").text = str(bbox[3] - bbox[1])

    watcher = Et.SubElement(Et.SubElement(watchzone, "Watches"), "Watcher")
    Et.SubElement(watcher, "Name").text = directory.stem

    watch_images = Et.SubElement(watcher, "WatchImages")

    for image_data in images:
        watch_image = Et.SubElement(watch_images, "WatchImage")
        relative_path = image_data['filepath'].relative_to(root_directory)
        Et.SubElement(watch_image, "FilePath").text = str(relative_path)
        logging.info(f"Added {image_data['filepath'].stem}.")
        mask_names.append(image_data['filepath'].stem)


def format_xml(elem, level=0):
    i = "\n" + level * "\t"

    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"

        for subelem in elem:
            format_xml(subelem, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def create_xml(all_image_data, root_directory):
    namespaces = {'xsd': "http://www.w3.org/2001/XMLSchema", 
                  'xsi': "http://www.w3.org/2001/XMLSchema-instance"}

    repository_link_comment = ("Generated using VAS File Architect: "
                               "https://github.com/phrayse/VAS-File-Architect ")
    error_metric_comment = ("ErrorMetric options: "
                            "default=PeakSignalToNoise | "
                            "MeanErrorPerPixel | "
                            "Absolute | "
                            "StructuralDissimilarity")

    game_profile = Et.Element("GameProfile", attrib={f"xmlns:{k}": v for k, v in namespaces.items()})
    game_profile.insert(0, Et.Comment(repository_link_comment))
    Et.SubElement(game_profile, "Name").text = root_directory.name

    screen = Et.SubElement(Et.SubElement(game_profile, "Screens"), "Screen")
    Et.SubElement(screen, "Name").text = "Game"

    geometry = Et.SubElement(screen, "Geometry")
    Et.SubElement(geometry, "Width").text = "1280"
    Et.SubElement(geometry, "Height").text = "720"

    watchzones = Et.SubElement(screen, "WatchZones")
    watchzones.insert(0, Et.Comment(error_metric_comment))

    grouped_images = group_images(all_image_data)
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

    format_xml(game_profile)

    try:
        tree = Et.ElementTree(game_profile)
        xml_bytes = BytesIO()
        # noinspection PyTypeChecker
        tree.write(xml_bytes, encoding="utf-8", xml_declaration=True)
        xml_content = xml_bytes.getvalue().decode("utf-8")
        return mask_names, xml_content
    except Exception as e:
        raise RuntimeError(f"Error generating XML file at {root_directory}: {e}")
