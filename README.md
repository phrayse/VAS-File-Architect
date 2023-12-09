# VAS-File-Architect

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Standalone Executable](#standalone-executable)
5. [Preparing Mask Images](#preparing-mask-images-for-vas-file-architect)
6. [Usage](#usage)
7. [Modules](#modules)
8. [Test Data](#test-data)
9. [Notes](#notes)
10. [Limitations](#limitations)
11. [Contributions and Feedback](#contributions-and-feedback)
12. [License](#license)

## Overview
VAS File Architect is a Python-based tool designed to streamline the creation of `.vas` (Video Auto Split) archives for use with ROMaster2's VideoAutoSplit component (https://github.com/ROMaster2/LiveSplit.VideoAutoSplit).  
It scans `.png` images to identify the non-transparent areas, crops each image to create a mask, generates `.xml` and `.asl` files based on various attributes of the masks, and compiles these assets into a `.vas` archive.

## Requirements
- Python 3.x
- PIL (Python Imaging Library)
- Tkinter (for GUI operations)

## Installation
Ensure Python 3.x is installed on your system. Install the required Python package PIL using pip:

```bash
pip install Pillow
```

Tkinter typically comes pre-installed with Python. If it's not present, refer to Tkinter installation guides based on your operating system.

## Standalone Executable
If installing Python doesn't sound appealing, download the standalone `VAS File Architect.exe` release.

## Preparing Mask Images for VAS File Architect
Creating effective mask images for use with VAS File Architect is a simple two-step process. Follow these guidelines to ensure your images are ready:
1. **Capture Screenshots for Masks:**
   - Use a screenshot tool (I use Toufool's AutoSplit (https://github.com/Toufool/AutoSplit)) to capture the scenes or elements from your game that you want to track. These screenshots will serve as the basis for your masks.

2. **Edit Screenshots to Create Reference Images:**
   - Open the screenshots in an image editing tool like GIMP (https://www.gimp.org).
   - Focus on the rectangular area you want to use as a mask. Remove the rest of the image, ensuring the areas you remove are completely transparent.
      - GIMP: Ensure the alpha channel is present. Rectangle select (hotkey R), invert selection (hotkey Ctrl+I), delete, export as `.png`.
   - **Important: Keep the original dimensions of the screenshot unchanged. Only the content should be altered, not the size.**

These reference images can now be processed by VAS File Architect to create the necessary files for your auto-splitting tool.

## Usage
1. **Prepare Target Directory:**
   - The target directory should be named after the game for which you're building the profile (e.g. "Final Fantasy").
   - Place the full-sized reference images in this directory. These images should primarily be transparent except for the areas of interest (masks).

2. **Run the Program:**
   - Execute `main.py`. The program prompts you to select the target directory using a GUI.

3. **Processing:**
   - The tool processes each `.png` image, identifying and cropping non-transparent areas.
   - It then generates a completed `structure.xml` file with WatchZones based on cropped areas, and a `script.asl` shell from a template.

4. **Output:**
   - The final output is a `.vas` archive in the target directory, containing cropped masks and the generated `.xml`/`.asl` files.
   - Note: The tool does not write the actual script part of the `.asl` file. This needs to be done by the user based on their specific requirements.

5. **Post-Processing:**
   - Open the `.vas` archive as you would a `.zip` or `.7z` archive.
   - Extract the `script.asl` file and implement your own code.
   - Copy your updated `script.asl` file back into the `.vas` archive.

## Modules
1. **main.py:** Orchestrates the entire workflow, from image processing to `.vas` archive creation.
2. **image_processing.py:** Handles image processing, specifically cropping non-transparent areas.
3. **xml_generation.py:** Generates `.xml` content for WatchZones based on processed image data.
4. **asl_generation.py:** Generates an `.asl` file from a template with recognised masks commented in for reference.
5. **vas_archive_generation.py:** Compiles processed images and generated `.xml`/`.asl` files into a `.vas` archive.

## Test Data
A `test-folder` is included in this repository to help you understand how the VAS File Architect works and to provide a quick way to test its functionality. This folder contains sample `.png` images and subdirectories with additional images. These samples are structured to mimic typical usage scenarios and can be used to test the image processing, `.xml` and `.asl` file generation, and `.vas` archive compilation steps of the tool.

Refer to the `README.md` within the `test-folder` for more details on the contents and how to use them for testing.

## Notes
- Logging is active and can be found in `app.log`.
- Ensure the target directory name matches the game name for which the profile is being created.
- Full-sized, primarily transparent `.png` images are required for effective mask identification.

## Limitations
- The tool assigns a unique WatchZone to each mask, even if multiple masks share identical bounding box coordinates.

## Contributions and Feedback
Contributions to the VAS File Architect are welcome! If you have suggestions or improvements, please feel free to contribute or message me directly.

## License
VAS File Architect is released under the MIT License. For more details, see the LICENSE file in the repository.