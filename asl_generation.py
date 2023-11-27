"""
ASL Generation for VAS File Architect
Generates an ASL (AutoSplit Language) template with a list of recognised masks for reference.

Functions:
  create_asl(mask_names): Generates ASL file content.
Parameters:
  mask_names (list of str): Recognised mask names from image processing.
Returns:
  asl_template (str): The contents of the ASL file, to be created directly within the VAS archive.
"""
def create_asl(mask_names):
  comment = f"""// Generated using VAS File Architect by Phrayse (fast@phrayse.au)
// https://github.com/phrayse/VAS-File-Architect
//
// Recognised masks:"""
  recognised_masks = "\n".join(f"// features[\"{mask_name}\"]" for mask_name in mask_names)

  asl_template = f"""{comment}
{recognised_masks}

startup
{{
  // Hint: Adjust timer settings such as refresh rate and Game Time/Real Time here
}}

init
{{
  // Hint: Declare any variables here
}}

start
{{
  // Hint: return features["main-menu"].old(100) > 90 && features["main-menu"].current < 80
}}

split
{{
  // Hint: return features["split-image"].current > 90
}}

reset
{{
  // Hint: Be careful with this one!
}}

isLoading
{{
  // Hint: return features["load-screen"].current > 90
}}"""
  return asl_template