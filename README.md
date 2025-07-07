# Dynamic-slideshow

## Aim of this work
The aim of this project is to automatically create a slideshow from a list of images, with the opportunity for anyone to contribute to this set. 
Once an image is added, the slideshow is updated seamlessly (no need to restart it).

The screenshot below illustrates how it looks like:
![image](Screenshot_slideshow.png)

## How it works
All guests are provided with a link (or QR code) to an online form, hosted on Tally, where they can freely upload photographs from their devices. 
A Python script iteratively downloads these images on a local folder, and creates a list of images as a JSON file.
In parallel, the slideshow, running on a web browser (HTML/Javascript code), reads the file list from the JSON file and 
displays the images. The file list is updated periodically to allow live updates.

## Features
As mentioned above, the slideshow is updated continuously. In addition, it provides the following features:
 - Displays a link and the associated QR code to the Tally's form used for sending the images
 - Displays the name of the contributor
 - A Not Safe For Work (NSFW) detector to avoid explicit content (pornography)

Every new image is added ontop of the file list, so that newly added files are read first.

## Installation
### Prerequities
#### Create a Tally form
Login/register to [Tally](https://tally.so/) and create a form with these two fields:
 - a file upload field
 - a short answer field

![image](Screenshot_fields.png)

Once it fits with all your needs, publish it. The share link will somehow https://tally.so/r/XXXXX where XXXXX denotes 
the form ID. Keep record of it.

#### Generate a Tally API token
In Tally's settings area, go to API key tab, and create a new API key.

#### Generate the QR code
Use the share link to Tally form to generate the associated QR code, and save it as an image. There are plenty of 
solution to do that, but I suggest using [Inkscape](https://inkscape.org/fr/) 
(see [here](https://www.youtube.com/watch?v=Ak_tYjtAKWc) for details).

### Configuration
Edit ``config.json``. The mandatory fields are:

 - ``tally_form_id``: ID of the associated form
 - ``tally_api_key``: Tally API key
 - ``watermarkText``: Text to display near the QR code
 - ``watermarkQR``: path to QR code image

Other options are available in this file, see below for details.

## Run the server
Once all the preceding steps are done, simply run ``main.py`` and keep it running in the background.

## Run the slideshow
The slideshow must be run in a web browser. **Don't try to open ``index.html`` directly, this won't work!**
This is because, for security reason, most web browsers disable the Javascript ``fetcth`` command when opening a local
file.

Instead, open a Python console, cd to the parent directory of ``index.html``, and run:

````bash
python -m http.server 8000
````

Then, open http://localhost:8000/index.html in your browser of choice.

## Optional parameters
The configuration file may contain the following optional arguments:
- ``imageList``: path to image/author list
- ``intervalSlideshow``: time interval between two displayed images (in seconds)
- ``intervalRefresh``: sets the duration for the slideshow the check if the file list has changed (in seconds)
- ``tally_refresh_period``: sets the waiting duration before updating the file list from Tally (in seconds)
- ``nsfw_filter``: Turn on/off the NSFW filter (must be ``true`` of ``false``)
- ``nsfw_max_value``: if the NSFW filter is on, sets the threshold value for explicit content detection; it must be 
between (allow everything) and 1 (forbid everything)
- ``nsfw_saved_model``: path to the trained model for NSFW detection. They can be downloaded on:
https://github.com/GantMan/nsfw_model/releases/tag/1.1.0