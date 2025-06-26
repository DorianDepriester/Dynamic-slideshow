import os
import requests
from nsfw_detector import predict
import json

NSFW_PATH = 'nsfw_flagged.json'

def form_link(formId):
    return f"https://tally.so/r/{formId}"

def fetch_tally_submissions(formId, api_key):
    url = f"https://api.tally.so/forms/{formId}/submissions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
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
    file_list = []
    for submission in responses['submissions']:
        submissionId = submission['id']
        for answer in submission['responses'][0]['answer']:
            if submissionId not in nsfw_list:
                url = answer['url']
                new_file, file_path = download_file(url, submissionId, path)
                if new_file:
                    nsfw_val = predict.classify(nsfw_model, file_path)[file_path]['porn']
                    print(f"NSFW score: {nsfw_val}")
                    if nsfw_val > nsfw_max:
                        nsfw_list.append(submissionId)
                        print('Explicit content detected! Submission {} has been flagged.'.format(submissionId))
                    else:
                        file_list.append(file_path)
                else:
                    file_list.append(file_path)
    with open(NSFW_PATH, "w", encoding="utf-8") as f:
        json.dump(nsfw_list, f, indent=2)
    return file_list