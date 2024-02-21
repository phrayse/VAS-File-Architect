# Demonstration Folder for VAS File Architect

This folder is set up to showcase the various functionalities of VAS File Architect.

## Contents

```
GameName
├── mps.png
├── GameName.vas (the built archive from this directory)
├── README.md (you are here!)
├── vasfa.log (the log file from building GameName.vas)
└── chapters
    ├── Box.png
    ├── Key.png
    ├── Necklace.png
    └── Ring.png
└── final
    ├── collector.png
    └── keeper.png
└── stage-clear
    ├── box.png
    ├── Box.png
    ├── finaleclear.png
    ├── keeper.jpg
    ├── keeper.png
    ├── Key.png
    ├── mid-edges.png
    ├── mps.png
    ├── NeckLace.png
    ├── stageclear.png
    ├── titleclear.png
    └── trbl-corners.png
```

## Purpose

- `GameName/`: Target directory; contains a single image.
The `.vas`, `.md`, and `.log` files are ignored.
- `/chapters/`: Four-image directory; all images sharing a group.
- `/final/`: Two-image directory; images close enough to group.
- `/stage-clear/`: Large amount of files to demonstrate multiple groupings by clustering.
    - `keeper.jpg` will be ignored.
    - `mid-edges.png` and `trbl-corners.png` are grouped together, demonstrating how 'bounding boxes' are only concerned with the corner points surrounding the minimum bounding rectangle of visible areas.
    - `box.png` will not be renamed, but `Box.png` will be: mask names must be unique throughout the directory, case-sensitive.

## Usage

To try it yourself:

1. Copy the `GameName` demonstration directory to your local device.
2. Run VAS File Architect using `GameName` as your target directory.
3. Inspect the generated `GameName.vas` archive and `vasfa.log` file.

