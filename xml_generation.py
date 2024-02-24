"""
XML Generation for VAS File Architect

Generates a formatted XML profile with distinct WatchZones created for each group.
"""
import logging
import xml.etree.ElementTree as Et
from collections import defaultdict
from io import BytesIO
from pathlib import Path


def group_images(all_image_data):
    """
    Groups images by shared corner clusters.

    :param list of dict all_image_data: Image data with filepaths and bounding boxes.
    :return: Grouped images as per bbox clusters.
    :rtype: defaultdict
    """
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
    """
    Enforce unique WatchZone names by appending a counter if name exists.

    :param str base_name: Original name for the WatchZone.
    :param set of str existing_names: Set of existing WatchZone names.
    :return: Unique WatchZone name.
    :rtype: str
    """
    if base_name not in existing_names:
        return base_name
    count = 1
    new_name = f"{base_name}_{count}"

    while new_name in existing_names:
        count += 1
        new_name = f"{base_name}_{count}"

    return new_name


def create_watchzone(params):
    """
    Creates individual WatchZone elements for each group.

    :param dict params: dict of image data to be stored in a WatchZone.
    """
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
    """
    Format an XML element and any children to a human-readable format by adding indents and newlines.

    :param Et.Element elem: XML element to be formatted.
    :param int level: Current level of indentation.
    """
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
    """
    Take all image data and generate a `structure.xml` file.

    :param list of dict all_image_data: dict of each image filepath, bbox, and cropped Image.
    :param Path root_directory: Target directory.
    :return: List of mask names and formatted XML content as a string.
    :rtype: tuple[list, str]
    :raise RuntimeError: if unable to write XML file to root directory.
    """
    namespaces = {'xsd': "http://www.w3.org/2001/XMLSchema", 
                  'xsi': "http://www.w3.org/2001/XMLSchema-instance"}

    repository_link = ("Generated using VAS File Architect: "
                       "https://github.com/phrayse/VAS-File-Architect ")
    error_metrics = ("ErrorMetric options: "
                     "default=PeakSignalToNoise | "
                     "MeanErrorPerPixel | "
                     "Absolute | "
                     "StructuralDissimilarity")

    game_profile = Et.Element("GameProfile", attrib={f"xmlns:{k}": v for k, v in namespaces.items()})
    game_profile.insert(0, Et.Comment(repository_link))
    Et.SubElement(game_profile, "Name").text = root_directory.name

    screen = Et.SubElement(Et.SubElement(game_profile, "Screens"), "Screen")
    Et.SubElement(screen, "Name").text = "Game"

    geometry = Et.SubElement(screen, "Geometry")
    Et.SubElement(geometry, "Width").text = "1280"
    Et.SubElement(geometry, "Height").text = "720"

    watchzones = Et.SubElement(screen, "WatchZones")
    watchzones.insert(0, Et.Comment(error_metrics))

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
