import os
import requests
from nsfw_detector import predict
import json
import time

NSFW_PATH = 'nsfw_flagged.json'

def form_link(formId):
    return f"https://tally.so/r/{formId}"

def fetch_tally_submissions(formId, api_key):
    url = f"https://api.tally.so/forms/{formId}/submissions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            break
        except requests.exceptions.ConnectionError:
            print('Connection lost. I will try reconnecting in 10 seconds.')
            time.sleep(10)
    return response.json()

def clear_tally_submissions(formId, api_key):
    response = fetch_tally_submissions(formId, api_key)
    for submission in response['submissions']:
        submissionId = submission['id']
        url = f"https://api.tally.so/forms/{formId}/submissions/{submissionId}"
        headers = {"Authorization": f"Bearer {api_key}"}
        requests.request("DELETE", url, headers=headers)

# Télécharge un fichier depuis une URL
def download_file(url, submissionId, dest_folder):
    filename = submissionId + '-' + url.split("/")[-1].split("?")[0]
    local_path = os.path.join(dest_folder, filename)
    new_file = False
    if not os.path.exists(local_path):
        new_file = True
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
        else:
            print(f"Download error : {url}")
    return new_file, local_path


def download_from_tally(path, form_id, api_key, nsfw_max, nsfw_model):
    if os.path.exists(NSFW_PATH):
        with open(NSFW_PATH, "r", encoding="utf-8") as f:
            nsfw_list = json.load(f)
    else:
        nsfw_list = []
    responses = fetch_tally_submissions(form_id, api_key)
    file_list = dict()
    for submission in responses['submissions']:
        submissionId = submission['id']
        author, images = [submission['responses'][i]['answer'] for i in range(2)]
        if isinstance(images, str): # If the author/images are switched
            images, author = author, images
        n_new_files = 0
        for answer in images:
            if submissionId not in nsfw_list:
                url = answer['url']
                new_file, file_path = download_file(url, submissionId, path)
                if new_file:
                    n_new_files += 1
                    if nsfw_model is not None:
                        nsfw_val = predict.classify(nsfw_model, file_path)[file_path]['porn']
                        print(f"NSFW score: {nsfw_val}")
                    else:
                        nsfw_val = 0.0
                    if nsfw_val > nsfw_max:
                        nsfw_list.append(submissionId)
                        print('Explicit content detected! Submission {} has been flagged.'.format(submissionId))
                    else:
                        file_list[file_path] = author
                else:
                    file_list[file_path] = author
        if n_new_files:
            print(f"{n_new_files} images added by {author}")
    with open(NSFW_PATH, "w", encoding="utf-8") as f:
        json.dump(nsfw_list, f, indent=2)
    return file_list