# VAS-File-Architect
## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start Guide](#quick-start-guide)
4. [Benefits](#benefits)
5. [Preparing Mask Images](#preparing-mask-images)
6. [Modules](#modules)
7. [Notes](#notes)
8. [FAQ or Troubleshooting](#faq-or-troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)

---

## Overview
[VAS File Architect](https://github.com/phrayse/VAS-File-Architect) is a comprehensive tool designed to streamline the creation of Video Auto Split (`.vas`) archives for use with [ROMaster2's VideoAutoSplit component](https://github.com/ROMaster2/LiveSplit.VideoAutoSplit).  
This program automates the process of generating a game profile (`structure.xml`), a template Auto Split Language (ASL) script (`script.asl`), and the final `.vas` archive containing all necessary files.

The primary focus of __VAS File Architect__ is to ensure that I never have to create another `structure.xml` file by hand again - and maybe help others avoid it too.

---

## Installation
### Cloning the Repository
To clone the repository, use the following command:

```bash
git clone https://github.com/phrayse/VAS-File-Architect.git
```
### Download Executable
Alternatively, you can download the executable directly from the Releases page on the GitHub repository.

---

## Quick Start Guide
1. Clone the repository or download the executable.
2. Prepare a directory with full-sized, primarily transparent `.png` images.
3. Run `main.py` or the executable.
4. Select the directory containing your images through the GUI.
5. The program will automatically process the images and generate the `.vas` archive.
6. Note: The generated `script.asl` file is a template and not a fully functional script. Modify it as needed to complete your ASL script based on your game's specific requirements.

---

## Benefits
### Easy Game Profile Creation:
The most significant advantage of using __VAS File Architect__ is its ability to automate the creation of complex game profiles, which are essential for use with the __Video Auto Split__ component.

### Automated Processing:
Once the target directory is selected, the program automatically:
- Groups images based on bounding box coordinates and their containing directory.
- Generates a `structure.xml` file, creating unique WatchZones for each group of images.
- Creates a skeleton `script.asl` file containing a list of recognized image masks and placeholders for script development.
- Compiles the processed images, `script.asl`, and `structure.xml` into a `.vas` archive.

### User-Friendly:
Through a simple GUI and an automated process, the tool aims to make creation of a `.vas` archive accessible to users regardless of their technical background.

---

## Preparing Mask Images
Effective mask images are crucial for accurate processing. Here's how to prepare them:

### Capture Screenshots for Masks:
Use a screenshot tool to capture scenes or elements from your game.  
These screenshots form the basis for your masks.

### Edit Screenshots to Create Masks:
Open the screenshots in an image editor like [GIMP](https://www.gimp.org).  
Focus on the area you want to track, ensuring other parts are completely transparent.  
Maintain the original dimensions of the screenshot.

---

## Modules
- `main.py`: Coordinates the overall workflow.  
- `image_processing.py`: Handles image cropping and grouping.  
- `xml_generation.py`: Generates game profile.  
- `asl_generation.py`: Creates an Auto Splitting Language script template.  
- `vas_archive_generation.py`: Compiles assets into a `.vas` archive.

---

## Notes
Logging is active and can be found in `app.log`.

---

## FAQ or Troubleshooting
*Q: The program fails to process my images. What can I do?*  
A: Ensure the images are not cropped, and are primarily transparent `.png` files. Check `app.log` for specific error messages.

*Q: How do I modify the ASL script?*  
A: Open the `script.asl` file from the `.vas` archive and customize the action blocks as per your specific requirements.

---

## Contributing
Contributions to the project are welcome. Feel free to submit a pull request or message me directly with feedback.

---

## License
__VAS File Architect__ is released under the MIT License. For more details, see the LICENSE file in the repository.
