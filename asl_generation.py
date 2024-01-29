"""
ASL Generation for VAS File Architect

Generates an AutoSplit Language (ASL) script skeleton.
It outlines basic script structure and includes a list of recognized masks from image
processing, serving as a template for development.

Functions:
    create_asl(mask_names):
        Generates the ASL file content.
        Arg:
            mask_names (list of str): Names of recognized masks from image processing.
        Returns:
            str: The generated ASL script content.
"""


def create_asl(mask_names):
    comment = ("// Generated using VAS File Architect: "
               "https://github.com/phrayse/VAS-File-Architect\n\n"
               "// Recognised masks:\n")
    recognised_masks = "\n".join(f"// features[\"{mask_name}\"]" for mask_name in mask_names)

    dict_of_actions = {
        "startup": "Setup initial settings like refresh rates or game-specific configurations.",
        "shutdown": "Executed when closing VASL, suitable for cleanup and saving state.",
        "init": "Initial logic, executed once before the update loop for setting initial variables.",
        "exit": "Executed when the script exits, for post-timer actions.",
        "update": "Continuous core logic of the script, executed first in each update cycle.",
        "start": "Defines start conditions for the timer, including value resets.",
        "split": "Triggers a split based on specific conditions, e.g., features[\"split-image\"].old > 90.",
        "reset": "Conditions to reset the timer. Use cautiously.",
        "isLoading": "Manages game time during load screens, e.g., return features[\"load-screen\"].current > 90",
        "gameTime": "Handles complex or game-specific game time calculations."
        # "undoSplit": "Not implemented in VAS"
    }

    asl = f"{comment}{recognised_masks}\n"

    for action in dict_of_actions:
        action_string = f"\n{action}\n{{\n\t// {dict_of_actions[action]}\n}}\n"
        asl += action_string

    return asl
