# from icoextract import IconExtractor
# from PIL import Image

# def extract_exe_icon(exe_path, output_path=None):
#     """
#     Extract icon from EXE file
#     :param exe_path: Path to the EXE file
#     :param output_path: Path to save the icon (optional)
#     :return: PIL Image object if output_path is None, otherwise None
#     """
#     extractor = IconExtractor(exe_path)
#     ico_path = exe_path + '.ico'
#     extractor.export_icon(ico_path)
    
#     with Image.open(ico_path) as img:
#         if output_path:
#             img.save(output_path)
#             return None
#         return img

# Example usage
# extract_exe_icon('laner.exe', 'icon.png')

#-------------- worked but tiny icon ----------------
# from PIL import Image
# import subprocess
# import os

# def get_exe_icon_pil(exe_path, output_path):
#     try:
#         # Use PowerShell to extract icon on Windows
#         ps_command = f'''
#         Add-Type -AssemblyName System.Drawing
#         $icon = [System.Drawing.Icon]::ExtractAssociatedIcon("{exe_path}")
#         $icon.ToBitmap().Save("{output_path}")
#         '''
        
#         subprocess.run(["powershell", "-Command", ps_command], 
#                       capture_output=True, text=True)
        
#         # Load and return the image
#         return Image.open(output_path)
        
#     except Exception as e:
#         print(f"Error: {e}")
#         return None

# get_exe_icon_pil = get_exe_icon_pil('laner.exe', 'icon.png')


#--------------------------- also worked but tiny icon ----------------
# import subprocess
# import sys
# import os

# def get_file_icon(file_path, output_path):
#     if sys.platform == "win32":
#         # Windows: Use PowerShell
#         cmd = f'''
#         Add-Type -AssemblyName System.Drawing
#         [System.Drawing.Icon]::ExtractAssociatedIcon("{file_path}").ToBitmap().Save("{output_path}")
#         '''
#         subprocess.run(["powershell", "-Command", cmd])
        
#     elif sys.platform == "darwin":
#         # macOS: Use sips command
#         subprocess.run(["sips", "-s", "format", "png", file_path, "--out", output_path])
        
#     else:
#         # Linux: More complex, might need custom solution
#         print("Linux icon extraction requires additional tools")

# get_file_icon('laner.exe', 'icon.png')


#--------------------------- also worked but tiny icon ----------------

# from PIL import Image
# import subprocess
# import os

# def get_exe_icon_pil(exe_path, output_path):
#     try:
#         # Use PowerShell to extract icon on Windows
#         ps_command = f'''
#         Add-Type -AssemblyName System.Drawing
#         $icon = [System.Drawing.Icon]::ExtractAssociatedIcon("{exe_path}")
#         $icon.ToBitmap().Save("{output_path}")
#         '''
        
#         subprocess.run(["powershell", "-Command", ps_command], 
#                       capture_output=True, text=True)
        
#         # Load and return the image
#         return Image.open(output_path)
        
#     except Exception as e:
#         print(f"Error: {e}")
#         return None
# get_exe_icon_pil('laner.exe', 'icon.png')

#------------------------------------ threading default exception handler ----------------


