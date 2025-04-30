import json
import requests
import os
import time  # Import the time module

def download_images_from_json(json_file, output_folder="images/all"):
    """
    Downloads images from URLs in a JSON file and updates the JSON with local filenames.
    Only downloads if the title is not null.  Includes a 10-second delay.

    Args:
        json_file: Path to the JSON file.
        output_folder: Directory to save the downloaded images.
    """

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'.")
        return

    # Create the output directory if it doesn't exist.  Handles nested directories.
    os.makedirs(output_folder, exist_ok=True)

    # Check if data is a list or a single dictionary
    if isinstance(data, list):
        data_list = data
    elif isinstance(data, dict):
        data_list = [data]  # Convert single object to a list
    else:
        print("Error: JSON data must be a list of objects or a single object.")
        return
    
    image_counter = 1
    updated_data = []  # Store the updated JSON objects


    for item in data_list:
        if not isinstance(item, dict):
            print("Warning: Skipping invalid item (not a dictionary).")
            continue # skip this item if it is not a dictionary

        title = item.get('title')
        image_url = item.get('image_url')

        # Check if title is not null AND image_url is present
        if title is not None and image_url:
            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()  # Raise an exception for bad status codes

                # Generate the filename
                filename = f"{image_counter:05d}.jpg"  # e.g., 00001.jpg
                filepath = os.path.join(output_folder, filename)

                # Download and save the image
                with open(filepath, 'wb') as image_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        image_file.write(chunk)

                # Update the JSON object with the filename
                item['image_file'] = filename
                updated_data.append(item)

                print(f"Downloaded and saved: {filename}")
                image_counter += 1

                # Wait for 10 seconds before the next download
                print("Waiting 5 seconds...")
                time.sleep(5)


            except requests.exceptions.RequestException as e:
                print(f"Error downloading image from {image_url}: {e}")
                updated_data.append(item) # Keep item even on failure
                continue
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                updated_data.append(item) # Keep item even on failure
                continue
        elif title is None:
            print(f"Skipping item due to null title: {item.get('image_url', 'No Image URL')}")
            updated_data.append(item)  # Keep the item in updated_data, even if skipped
        elif image_url is None:  # This condition isn't strictly necessary now, but is good for completeness
            print(f"Skipping item due to missing image_url: {item.get('title', 'Untitled')}")
            updated_data.append(item) # Keep the item even if skipped.

    # Save the updated JSON data
    output_json_path = os.path.join(os.path.dirname(json_file), "updated_" + os.path.basename(json_file)) #save in same directory as input file
    try:
        with open(output_json_path, 'w', encoding='utf-8') as outfile:
            json.dump(updated_data, outfile, indent=4, ensure_ascii=False)  # Use indent for readability, ensure_ascii for non-ASCII characters
        print(f"Updated JSON data saved to: {output_json_path}")
    except Exception as e:
        print(f"Failed to save the updated JSON: {e}")



if __name__ == '__main__':

    download_images_from_json('artworks.json')
