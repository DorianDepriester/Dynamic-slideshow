# Dynamic-slideshow

## Aim of this work
The aim of this project is to automatically create a slideshow from a list of images, with the opportunity for anyone to contribute to this set. 
Once an image is added, the slideshow is updated seamlessly (no need to restart it)

## How it works
All guests are provided with a link (or QR code) to an online form, hosted on Tally, where they can freely upload photographs from their devices. 
A Python script iteratively downloads these images on a local folder, and creates a list of images a JSON file.
In parallel, the slideshow, running on a web browser (HTML code), reads the file list from the JSON file and displays the images. 
The file list is updated periodically to allow live updates.

Note : every new image is added ontop of the file list, so that newly added files are read first.

## Configuration
### Prerequities
#### Create a Tally form
Login/register to [Tally](https://tally.so/) and create a form with one single file upload menu:
![image](https://github.com/user-attachments/assets/7471e6e3-e417-4d36-ad9b-3aa12aae6ad4)

Once it fits with all your needs, publish it. The share link will ressemble to https://tally.so/r/XXXXX where XXXXX denotes the form ID. Keep record of it.

#### Generate a Tally API token
In Tally's settings area, go to API key tab, and create a new API key
