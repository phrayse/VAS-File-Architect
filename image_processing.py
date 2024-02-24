"""
Image Processing for VAS File Architect

Handles image grouping and cropping. Utilises a breadth-first search to chain corner
points together into clusters if they fall within a defined tolerance distance.
"""
import logging
from collections import defaultdict
from pathlib import Path

from PIL import Image


def extract_corners(filepath):
    """
    Extract the top-left and bottom-right corners of an image's bounding box.

    :param Path filepath: Path to the image file.
    :return: Top-left coords, bottom-right coords, and directory of the image.
    :rtype: tuple[tuple[int,int], tuple[int,int], Path] or None
    :raise IOError: if unable to access filepath.
    """
    try:
        with Image.open(filepath) as img:
            if img.mode != 'RGBA':
                logging.info(f"Converting {filepath.stem} from {img.mode} to RGBA.")
                img = img.convert('RGBA')

            bbox = img.getbbox()

            if bbox:
                tl_corner = (bbox[0], bbox[1])
                br_corner = (bbox[2], bbox[3])
                directory = filepath.parent
                logging.info(f"{filepath.stem}: tl: {tl_corner}, br: {br_corner}, dir: {directory}")
                return tl_corner, br_corner, directory

            logging.warning("No non-transparent area found in image.")
            return None, None, None

    except IOError as e:
        logging.error(f"IOError while accessing {filepath}: {e}")
        return None, None, None
    except Exception as e:
        logging.error(f"Unexpected error while processing file {filepath}: {e}")
        return None, None, None


def is_within_tolerance(corner, other_corner, tolerance):
    """
    Calculate distance between two points on a plane,
    check whether the result falls within the tolerance distance.

    :param tuple[int, int] corner: x,y coords of a corner.
    :param tuple[int, int] other_corner: x,y coords of the other corner.
    :param int tolerance: maximum distance in pixels to be considered neighbours.
    :return: True if distance <= tolerance.
    :rtype: bool
    """
    distance = ((corner[0] - other_corner[0]) ** 2 + (corner[1] - other_corner[1]) ** 2) ** 0.5
    return distance <= tolerance


def bfs_cluster_corners(corners, tolerance):
    """
    Breadth-first search to label every corner point with a cluster ID.
    Each point within tolerance is considered a neighbour and added to the queue.
    This function is called separately for the lists of tl and br corners.

    :param list of (tuple[int, int]) corners: list of x,y coords of corners.
    :param int tolerance: maximum distance in pixels between neighbours.
    :return: Mapped list of cluster labels to filepaths.
    :rtype: list
    """
    cluster_id = 0
    clusters = [-1] * len(corners)
    for i in range(len(corners)):
        if clusters[i] != -1:
            continue

        queue = [i]
        while queue:
            current = queue.pop(0)
            clusters[current] = cluster_id

            for j, other_corner in enumerate(corners):
                if clusters[j] == -1 and is_within_tolerance(corners[current], corners[j], tolerance):
                    queue.append(j)

        cluster_id += 1

    return clusters


def calculate_mbr_for_group(bboxes):
    """
    Calculate the minimum bounding rectangle for a group of images.

    :param list of tuple bboxes: Bounding boxes of all images in a group.
    :return: min_x0, min_y0, max_x1, max_y1
    :rtype: tuple[int, int, int, int]
    """
    min_x0 = min(bbox[0][0] for bbox in bboxes)
    min_y0 = min(bbox[0][1] for bbox in bboxes)
    max_x1 = max(bbox[1][0] for bbox in bboxes)
    max_y1 = max(bbox[1][1] for bbox in bboxes)

    logging.info(f"Calculated MBR: {min_x0, min_y0, max_x1, max_y1}")
    return min_x0, min_y0, max_x1, max_y1


def crop_image(filepath, bbox=None):
    """
    Crop a given image based on the specified bounding box.

    :param Path filepath: File path to the image.
    :param tuple[int,int,int,int] bbox: Bounding box coordinates (x0, y0, x1, y1).
    :return: Bbox coords and cropped image.
    :rtype: tuple[tuple[int,int,int,int],Image.Image]
    :raise IOError: if unable to access filepath.
    :raise Exception:
    """
    try:
        with Image.open(filepath) as img:
            if img.mode != 'RGBA':
                logging.info(f"Converting {filepath.stem} from {img.mode} to RGBA for processing.")
                img = img.convert('RGBA')

            if not bbox:
                bbox = img.getbbox()

            if bbox:
                cropped_img = img.crop(bbox)
                logging.info(f"Image cropped: {filepath.stem}")
                return bbox, cropped_img
            else:
                logging.warning(f"No non-transparent area found in {filepath}")
                return None

    except IOError as e:
        logging.error(f"IOError while accessing {filepath}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error while processing file {filepath}: {e}")
        return None


def group_images_by_clusters(dir_filepaths, filepath_to_corners, tl_clusters, br_clusters):
    """
    Assigns images to groups by combining the cluster IDs of top-left corners and bottom-right corners.
    Images which share both tl and br clusters are grouped together.

    :param list of Path dir_filepaths: File paths in a directory.
    :param dict filepath_to_corners: Mapping file paths to their corners.
    :param list tl_clusters: Cluster labels for top-left corners.
    :param list br_clusters: Cluster labels for bottom-right corners.
    :return: Dict of created groups
    :rtype: defaultdict
    """
    grouped_images = defaultdict(list)

    logging.info("Grouping images as per clusters.")
    for i, filepath in enumerate(dir_filepaths):
        tl_cluster = tl_clusters[i]
        br_cluster = br_clusters[i]
        directory = filepath_to_corners[filepath][2]
        grouped_images[(tl_cluster, br_cluster, directory)].append(filepath)
        logging.info(f"{filepath.stem} added to group: ({tl_cluster},{br_cluster}).")

    logging.info(f"Formed {len(grouped_images)} image groups.")
    return grouped_images


def enforce_unique_name(base_name, existing_names):
    """
    Enforce unique names for image masks.

    :param str base_name: Original name for the image file.
    :param set of str existing_names: Set of existing names.
    :return: A unique name for the image mask.
    :rtype: str
    """
    if base_name not in existing_names:
        return base_name

    count = 1
    new_name = f"{base_name}_{count}"

    while new_name in existing_names:
        count += 1
        new_name = f"{base_name}_{count}"

    logging.info(f"{base_name} relabelled as {new_name}")
    return new_name


def process_all_images(filepaths):
    """
    Extracts a list of all top-left corner coords, a list of all bottom-right corner coords, and performs a
    breadth-first search on these to create groups of all corners which fall within a tolerance distance of another.

    Images are grouped if they share both a top-left and bottom-right cluster ID.The minimum
    bounding rectangle for each group is calculated, which is to replace the original bounding box of each
    image in the group.

    Images are cropped to their updated bbox and checked to ensure each name is unique.

    :param list of Path filepaths: A list of file paths to the images.
    :return: Tuple of all processed image data and all skipped image files.
    :raise Exception:
    """
    filepath_to_corners = {}
    directory_to_filepaths = defaultdict(list)

    for filepath in filepaths:
        tl, br, directory = extract_corners(filepath)
        if tl and br:
            filepath_to_corners[filepath] = (tl, br, directory)
            directory_to_filepaths[directory].append(filepath)

    all_grouped_images = {}
    tolerance = 10  # Maximum distance in pixels between neighbouring points. Lower this value for tighter clusters.

    for directory, dir_filepaths in directory_to_filepaths.items():
        logging.info(f"Processing: {directory.parts[-1]}")

        try:
            logging.info("Beginning BFS.")
            tl_corners = [filepath_to_corners[fp][0] for fp in dir_filepaths]
            br_corners = [filepath_to_corners[fp][1] for fp in dir_filepaths]

            tl_clusters = bfs_cluster_corners(tl_corners, tolerance)
            br_clusters = bfs_cluster_corners(br_corners, tolerance)

            grouped_images = group_images_by_clusters(dir_filepaths, filepath_to_corners, tl_clusters, br_clusters)
            all_grouped_images.update(grouped_images)

        except Exception as e:
            logging.error(f"Error processing images in directory {directory}: {e}")

    logging.info("Completed image grouping. Updating bounding boxes.")

    for group, group_filepaths in all_grouped_images.items():
        try:
            bboxes = [filepath_to_corners[filepath][:2] for filepath in group_filepaths]
            mbr = calculate_mbr_for_group(bboxes)

            for filepath in group_filepaths:
                filepath_to_corners[filepath] = mbr

        except Exception as e:
            logging.error(f"Error updating bounding boxes for group {group}: {e}")

    all_image_data, skipped_files = [], []
    existing_names = set()

    for filepath in filepaths:
        try:
            updated_bbox = filepath_to_corners.get(filepath, None)

            if updated_bbox:
                result = crop_image(filepath, updated_bbox)

                if result:
                    bbox, cropped_img = result

                    unique_name = enforce_unique_name(filepath.stem, existing_names)
                    existing_names.add(unique_name)
                    filepath = filepath.with_stem(str(unique_name))

                    image_data = {'filepath': filepath, 'bbox': bbox, 'cropped_img': cropped_img}
                    all_image_data.append(image_data)
                else:
                    logging.warning(f"Skipping image: {filepath.stem}")
                    skipped_files.append(filepath)

        except Exception as e:
            logging.error(f"Error processing image {filepath}: {e}")
            skipped_files.append(filepath)

    logging.info("Image processing completed.")
    return all_image_data, skipped_files
