"""
Image Processing for VAS File Architect

Handles image grouping and cropping for the VAS File Architect. It groups images by
shared bounding box coordinates using DBSCAN clustering for directories with more than
two images and a proximity check for two-image directories. Images in single-image
directories are processed individually.

Functions:
    process_all_images(filepaths):
        Groups images by bounding box proximity and processes each image.
        Arg:
            filepaths (list of Path): A list of file paths to the images.
        Returns:
            tuple: Contains processed image data and list of skipped files.

    process_image(filepath, bbox):
        Crops a given image based on the specified bounding box.
        Arg:
            filepath (Path): File path to the image.
            bbox (tuple): Bounding box with coordinates (x0, y0, x1, y1).
        Returns:
            tuple: Bounding box and cropped image, or None if not processed.

    extract_corners(filepath):
        Extracts the top-left and bottom-right corners of an image's bounding box.
        Arg:
            filepath (Path): File path to the image.
        Returns:
            tuple: Top-left and bottom-right corners, and the directory of the image.

    are_images_close(corners1, corners2, tolerance):
        Determines if two images are close based on corner coordinates.
        Arg:
            corners1 (tuple): Corners of the first image.
            corners2 (tuple): Corners of the second image.
            tolerance (int): Tolerance level for proximity.
        Returns:
            bool: True if images are close, False otherwise.

    apply_dbscan_to_corners(corners, epsilon):
        Applies DBSCAN clustering to image corners.
        Arg:
            corners (ndarray): Array of corner coordinates.
            epsilon (int): The maximum distance between two samples for clustering.
        Returns:
            ndarray: Cluster labels for each corner.

    group_images_by_clusters(dir_filepaths, filepath_to_corners, tl_clusters, br_clusters):
        Groups image file paths based on DBSCAN clustering results.
        Arg:
            dir_filepaths (list of Path): File paths in a directory.
            filepath_to_corners (dict): Mapping file paths to their corners.
            tl_clusters (ndarray): Cluster labels for top-left corners.
            br_clusters (ndarray): Cluster labels for bottom-right corners.
        Returns:
            defaultdict: Grouped image file paths by cluster and directory.

    calculate_mbr_for_group(bboxes):
        Calculates the minimum bounding rectangle for a group of images.
        Arg:
            bboxes (list of tuple): Bounding boxes of the images.
        Returns:
            tuple: Coordinates of the minimum bounding rectangle.

    enforce_unique_name(base_name, existing_names):
        Ensures unique mask names.
        Arg:
            base_name (str): The base name for the image mask.
            existing_names (set of str): Set of existing mask names to avoid duplicates.
        Returns:
            str: A unique name for the image mask.
"""
import logging
from collections import defaultdict

import numpy as np
from PIL import Image
from sklearn.cluster import DBSCAN


def process_all_images(filepaths):
    filepath_to_corners = {}
    directory_to_filepaths = defaultdict(list)

    for filepath in filepaths:
        tl, br, directory = extract_corners(filepath)
        if tl and br:
            filepath_to_corners[filepath] = (tl, br, directory)
            directory_to_filepaths[directory].append(filepath)

    all_grouped_images = {}
    tolerance = 10  # Maximum distance in pixels between neighbouring points.

    for directory, dir_filepaths in directory_to_filepaths.items():
        logging.info(f"Processing: {directory.parts[-1]}")

        try:
            if len(dir_filepaths) == 1:
                logging.info(f"One image file located.")
                all_grouped_images[(0, 0, directory)] = [dir_filepaths[0]]
            elif len(dir_filepaths) == 2:
                logging.info(f"Two image files located.")
                filepath1, filepath2 = dir_filepaths

                if are_images_close(filepath_to_corners[filepath1], filepath_to_corners[filepath2], tolerance):
                    logging.info("Grouping images due to proximity.")
                    all_grouped_images[(0, 0, directory)] = dir_filepaths
                else:
                    all_grouped_images[(0, 0, directory)] = [dir_filepaths[0]]
                    all_grouped_images[(0, 1, directory)] = [dir_filepaths[1]]
            else:
                logging.info("Beginning DBSCAN clustering.")
                tl_corners = [filepath_to_corners[fp][0] for fp in dir_filepaths]
                br_corners = [filepath_to_corners[fp][1] for fp in dir_filepaths]

                tl_clusters = apply_dbscan_to_corners(np.array(tl_corners), epsilon=tolerance)
                br_clusters = apply_dbscan_to_corners(np.array(br_corners), epsilon=tolerance)

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
                result = process_image(filepath, updated_bbox)

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


def process_image(filepath, bbox=None):
    try:
        with Image.open(filepath) as img:
            if img.mode != 'RGBA':
                logging.info(f"Converting {filepath.stem} from {img.mode} to RGBA for processing.")
                img = img.convert('RGBA')

            if not bbox:
                bbox = img.getbbox()

            if bbox:
                cropped_img = img.crop(bbox)
                logging.info(f"Image processed: {filepath.stem}")
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


def extract_corners(filepath):
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


def are_images_close(corners1, corners2, tolerance):
    tl_diff = abs(corners1[0][0] - corners2[0][0]) <= tolerance and abs(corners1[0][1] - corners2[0][1]) <= tolerance
    br_diff = abs(corners1[1][0] - corners2[1][0]) <= tolerance and abs(corners1[1][1] - corners2[1][1]) <= tolerance
    return tl_diff and br_diff


def apply_dbscan_to_corners(corners, epsilon):
    clustering = DBSCAN(eps=epsilon, min_samples=1).fit(corners)
    logging.info(f"DBSCAN results: {clustering.labels_}")
    return clustering.labels_


def group_images_by_clusters(dir_filepaths, filepath_to_corners, tl_clusters, br_clusters):
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


def calculate_mbr_for_group(bboxes):
    min_x0 = min(bbox[0][0] for bbox in bboxes)
    min_y0 = min(bbox[0][1] for bbox in bboxes)
    max_x1 = max(bbox[1][0] for bbox in bboxes)
    max_y1 = max(bbox[1][1] for bbox in bboxes)

    logging.info(f"Calculated MBR: {min_x0, min_y0, max_x1, max_y1}")
    return min_x0, min_y0, max_x1, max_y1


def enforce_unique_name(base_name, existing_names):
    if base_name not in existing_names:
        return base_name

    count = 1
    new_name = f"{base_name}_{count}"

    while new_name in existing_names:
        count += 1
        new_name = f"{base_name}_{count}"

    logging.info(f"{base_name} relabelled as {new_name}")
    return new_name
