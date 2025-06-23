import os
import requests

def formlink(formId):
    return f"https://tally.so/r/formId"

def fetch_tally_responses(formId, api_key):
    url = f"https://api.tally.so/forms/{formId}/submissions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# Télécharge un fichier depuis une URL
def download_file(url, dest_folder):
    filename = url.split("/")[-1].split("?")[0]
    local_path = os.path.join(dest_folder, filename)
    if not os.path.exists(local_path):
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
            print(f"New file downloaded: {filename}")
        else:
            print(f"Download error : {url}")

def download_from_tally(path, form_id, api_key):
    responses = fetch_tally_responses(form_id, api_key)
    for response in responses['submissions']:
        for answer in response['responses'][0]['answer']:
            url = answer['url']
            download_file(url, path)