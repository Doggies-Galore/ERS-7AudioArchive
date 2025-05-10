import os
import shutil

# Define the keyword-to-folder mapping
keywords = ["dance", "sp", "search", "quest", "charge", "consent", "pc", "wc", "bone", "ball","other","game"]

# Get the current working directory (where the script is run)
base_dir = os.getcwd()

# Source directory
source_dir = os.path.join(base_dir, "SegmentedAudio")

# Ensure the source directory exists
if not os.path.exists(source_dir):
    raise FileNotFoundError(f"Source directory not found: {source_dir}")

# Process each file in the source directory
for filename in os.listdir(source_dir):
    file_path = os.path.join(source_dir, filename)
    
    # Skip if not a file
    if not os.path.isfile(file_path):
        continue
    
    # Check each keyword to determine where to copy the file
    for keyword in keywords:
        if keyword in filename.lower():
            target_dir = os.path.join(base_dir, keyword)
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(file_path, target_dir)
            break  # Stop after the first match

print("File organization complete.")
