import os
import json
import time
from tally import download_from_tally

def dyn_slideshw_server(conf_file="config.json"):
    with open(conf_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Load configuration file
    json_path = config.get("imageList", "images.json")
    image_folder = config.get("imageFolder", "images")
    time_period = config.get("tally_refresh_period", 10)
    form_id = config.get("tally_form_id", '')

    api_key = os.getenv('TALLY_API_KEY')
    api_key = config.get("tally_api_key", api_key)
    if api_key == '':
        raise ValueError('TALLY_API_KEY must be set as environment variable '
                         'or defined in configuration file as "tally_api_key".')

    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif')

    # If not present, create destination folder
    os.makedirs(image_folder, exist_ok=True)

    msg = 'I am now continuously checking out the content of:'
    msg += '\n  -folder named "{}"'.format(image_folder)
    msg += '\n  -Tally\'s form with ID {}'.format(form_id)
    print(msg)
    print('Type Ctrl+C to stop me. You can now run the slideshow.')

    while True:
        # Load existing list file, if any
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                old_list = json.load(f)
        else:
            old_list = []

        # Fetch images from Tally's form
        download_from_tally(image_folder, form_id, api_key)

        # List all images in local dir
        current_files = [
            os.path.join(image_folder, f).replace("\\", "/")
            for f in os.listdir(image_folder)
            if f.lower().endswith(valid_extensions)
        ]

        # New files found in the dir
        new_files = [f for f in current_files if f not in old_list]

        # Update file list
        new_list = new_files + [f for f in old_list if f in current_files]

        # Save file list as json
        if new_files:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(new_list, f, indent=2)

            print(f"{len(new_files)} new image(s) added to the list")
        time.sleep(time_period)

if __name__ == "__main__":
    dyn_slideshw_server()