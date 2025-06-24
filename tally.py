import os
import requests
from nsfw_detector import predict
model = predict.load_model('mobilenet_v2_140_224/saved_model.h5')

def formlink(formId):
    return f"https://tally.so/r/formId"

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
def download_file(url, dest_folder):
    filename = url.split("/")[-1].split("?")[0]
    local_path = os.path.join(dest_folder, filename)
    nsfw_val = 0.
    if not os.path.exists(local_path):
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
            nsfw_val = predict.classify(model, local_path)[local_path]['porn']
            print(f"NSFW score: {nsfw_val}")
        else:
            print(f"Download error : {url}")
    return nsfw_val, local_path


def download_from_tally(path, form_id, api_key, nsfw_max):
    responses = fetch_tally_submissions(form_id, api_key)
    for submission in responses['submissions']:
        for answer in submission['responses'][0]['answer']:
            url = answer['url']
            nsfw_val, file_path = download_file(url, path)
            if nsfw_val > nsfw_max:
                submissionId = submission['id']
                url = f"https://api.tally.so/forms/{form_id}/submissions/{submissionId}"
                headers = {"Authorization": f"Bearer {api_key}"}
                requests.request("DELETE", url, headers=headers)
                print('Explicit content detected in submission {}'.format(submissionId))
                new_path = file_path + '.nsfw'
                os.rename(file_path, new_path)
                print('I have deleted the submission and excluded the file from the list.')
                break