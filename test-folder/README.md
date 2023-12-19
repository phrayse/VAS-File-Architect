# Test Folder for VAS File Architect

This folder features example image masks contained within multiple subdirectories.

## Contents

- `mps.png`: A sample image at the root of the test folder.
- `mps0.png`: An exact duplicate of `mps.png`.
- `final/`: A subfolder containing two images (`final1.png` and `final2.png`).
- `split/`: A subfolder containing four images (`Box.png`, `Key.png`, `Necklace.png`, and `Ring.png`).
  - `Necklace.png` and `Ring.png` share identical coordinates.

Each of these images is intended to showcase the tool's ability to process individual images in the main directory and any subdirectories.

## Usage

To use these test images:

1. Copy the `test-folder` to your chosen directory.
2. Run the VAS File Architect tool and select this copied `test-folder` as your target directory.
3. Observe how the tool processes these images, generates XML and ASL files, and compiles them into a VAS archive.
