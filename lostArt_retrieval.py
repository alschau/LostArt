import csv
import requests
from bs4 import BeautifulSoup
import os
import time
import re

def download_images_from_csv(csv_file, output_folder="images/lostart"):
    """
    Downloads images from webpages linked in a CSV file.

    Args:
        csv_file: Path to the CSV file.
        output_folder: Directory to save the downloaded images.
    """

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')  # Use DictReader for easier access

            # Create the output directory if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            for row in reader:
                # --- Debugging Prints (Keep these for now) ---
                # print(f"Raw row: {row}")
                if not any(row.values()):
                    # print("Skipping empty row.")
                    continue
                # -----------------------------------------------

                art_id = row.get("Lost Art ID")
                link = row.get("Link")

                # --- Debugging Prints ---
                # print(f"Lost Art ID: {art_id}")
                # print(f"Link: {link}")
                # ------------------------

                if not art_id or not link:
                    print(f"Skipping row: Missing 'Lost Art ID' or 'Link'.")
                    continue

                try:
                    # Fetch the webpage content
                    response = requests.get(link)
                    response.raise_for_status()

                    # Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find the image tag.  Use a more robust selector.
                    img_tag = soup.find('img', src=re.compile(r'/sites/default/files/attachment/image/.*\.jpg'))


                    if img_tag:
                        # Construct the full image URL
                        image_url = "https://www.lostart.de" + img_tag['src']


                        # Download the image
                        image_response = requests.get(image_url, stream=True)
                        image_response.raise_for_status()

                        # Save the image
                        filename = f"{art_id}.jpg"
                        filepath = os.path.join(output_folder, filename)
                        with open(filepath, 'wb') as image_file:
                            for chunk in image_response.iter_content(chunk_size=8192):
                                image_file.write(chunk)

                        print(f"Downloaded image for ID {art_id}: {filename}")
                        time.sleep(3) # delay
                    else:
                        print(f"No image found for ID {art_id} on {link}")

                except requests.exceptions.RequestException as e:
                    print(f"Error processing ID {art_id}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred for ID {art_id}: {e}")

    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == '__main__':

    for i in range(17):
        download_images_from_csv("Datasets/LostArtDataset/lostart-export ("+str(i+2)+").csv")