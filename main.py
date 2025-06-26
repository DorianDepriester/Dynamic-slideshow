import os
import json
import time

from tally import download_from_tally, clear_tally_submissions
from nsfw_detector import predict


def dyn_slideshw_server(conf_file="config.json"):
    with open(conf_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Load configuration file
    json_path = config.get("imageList", "images.json")
    image_folder = config.get("imageFolder", "images")
    time_period = config.get("tally_refresh_period", 10)
    interval_slideshow = config.get("intervalSlideshow", 10)
    form_id = config.get("tally_form_id", '')

    api_key = os.getenv('TALLY_API_KEY')
    api_key = config.get("tally_api_key", api_key)
    if api_key == '':
        raise ValueError('TALLY_API_KEY must be set as environment variable '
                         'or defined in configuration file as "tally_api_key".')

    nsfw_saved_model = config.get("nsfw_saved_model", '')
    nsfw_max = config.get("nsfw_max", 0.5)
    model = predict.load_model(nsfw_saved_model, compile=False)

    # If not present, create destination folder
    os.makedirs(image_folder, exist_ok=True)

    msg = 'I will now be continuously checking out the content of:'
    msg += '\n  - folder named "{}"'.format(image_folder)
    msg += '\n  - Tally\'s form with ID {}'.format(form_id)
    print(msg)

    a = input('Do you want me to clear the Tally\'s submissions before I start (y/n)? ')
    if a.lower() == 'y':
        clear_tally_submissions(form_id, api_key)

    ls = os.listdir(image_folder)
    if ls:
        a = input(f"{len(ls)} image(s) found in local directory. Delete it/them before continuing (y/n)? ")
        if a.lower() == 'y':
            for f in ls:
                os.remove(os.path.join(image_folder, f))

    print('Type Ctrl+C to stop me. You can now run the slideshow.')
    while True:
        # Load existing list file, if any
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                old_list = json.load(f)
        else:
            old_list = dict()

        # Fetch images from Tally's form
        new_list = download_from_tally(image_folder, form_id, api_key, nsfw_max, model)

        # Count number of added/removed files
        n_new_files = len([f for f in new_list.keys() if f not in old_list.keys()])
        n_rem_files = len([f for f in old_list.keys() if f not in new_list.keys()])

        # Save file list as json
        if not (new_list == old_list):
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(new_list, f, indent=2)
            if n_new_files:
                print(f"{n_new_files} new image(s) added to the list")
            if n_rem_files:
                print(f"{n_rem_files} image(s) removed from the list")
            print(f"The list now contains {len(new_list)} image(s)")

        actual_time_period = max([time_period, n_new_files * interval_slideshow])
        time.sleep(actual_time_period)

if __name__ == "__main__":
    dyn_slideshw_server()