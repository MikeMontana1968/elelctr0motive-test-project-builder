import os
import json
from pathlib import Path

def parse_folder_name(folder_name):
    """
    Parse folder name in format 'Make Model Year'
    Example: 'Acura Integra Type R 2001'
    Returns: (make, model, year)
    """
    parts = folder_name.split()
    
    # Last part should be the year
    year = parts[-1]
    
    # First part is the make
    make = parts[0]
    
    # Everything in between is the model
    model = ' '.join(parts[1:-1])
    
    return make, model, year

def build_car_dataset(root_folder, output_json='car_dataset.json'):
    """
    Enumerate through folders and build a JSON dataset of car images.
    
    Args:
        root_folder: Path to the root directory containing car folders
        output_json: Output JSON file name
    """
    # Image file extensions to look for
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    dataset = []
    
    # Walk through the directory structure
    for root, dirs, files in os.walk(root_folder):
        # Skip the root folder itself
        if root == root_folder:
            continue
        
        # Get the folder name (last part of the path)
        folder_name = os.path.basename(root)
        
        try:
            # Parse the folder name to extract make, model, year
            make, model, year = parse_folder_name(folder_name)
            
            # Process each file in the folder
            i:int = 0
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                i += 1
                # Check if it's an image file
                if file_ext in image_extensions:
                    full_path = os.path.join(root, file)
                    
                    # Add entry to dataset
                    dataset.append({
                        'make': make,
                        'model': model,
                        'year': year,
                        'file_path': full_path
                    })
                if i >= 5:
                    break
            
        except Exception as e:
            print(f"Error processing folder '{folder_name}': {e}")
            continue
    
    # Write to JSON file
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Dataset created successfully!")
    print(f"Total images: {len(dataset)}")
    print(f"Output file: {output_json}")
    
    # Print some statistics
    makes = set(entry['make'] for entry in dataset)
    print(f"Unique makes: {len(makes)}")
    
    return dataset

if __name__ == "__main__":    
    root_folder = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(root_folder):
        print(f"Root folder '{root_folder}' does not exist. Please check the path.")
        exit(1)

    dataset = build_car_dataset(root_folder, os.path.join(root_folder, "../vehicle-images/", "car_dataset.json"))
    
    # Optional: Print first few entries as preview
    print("\nSAMPLE First 3 entries")
    for entry in dataset[:3]:
        print(entry)