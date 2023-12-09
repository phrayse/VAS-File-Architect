"""
ASL Generation for VAS File Architect
Generates a skeleton ASL (AutoSplit Language) file from a template.
Includes a list of recognised masks for easy reference.

Functions:
  create_asl(mask_names): Generates ASL file content.
Parameters:
  mask_names (list of str): Recognised mask names from image processing.
Returns:
  asl_template (str): The contents of the ASL file, to be created directly within the VAS archive.
"""
def create_asl(mask_names):
  comment = "// Generated using VAS File Architect: https://github.com/phrayse/VAS-File-Architect\n\n// Recognised masks:\n"
  recognised_masks = "\n".join(f"// features[\"{mask_name}\"]" for mask_name in mask_names)

  # Dictionary of actions recognised by VAS, excluding exit, gameTime, and shutdown.
  dict_of_actions = {
    "startup": "Initialise settings here: gametime/realtime; refresh rate, etc.",
    "init": "Declare any variables here.",
    "start": "Start conditions; reset any required values here.",
    "update": "Core logic - this block runs first in each iteration.",
    "split": "Split conditions. ex: return features[\"split-image\"].old > 90",
    "undoSplit": "Careful!",
    "reset": "Careful!",
    "isLoading": "Boolean, controls game time. ex: return features[\"load-screen\"].current > 90",
  }

  # Compile .asl contents
  asl_template = f"{comment}{recognised_masks}\n"
  for action in dict_of_actions:
    action_string = f"\n{action}\n{{\n\t// {dict_of_actions[action]}\n}}\n"
    asl_template += action_string

  return asl_template