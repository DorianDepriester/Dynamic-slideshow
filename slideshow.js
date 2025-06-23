let config = {};
let images = [];
let current = 0;
let updating = false;

async function loadConfig() {
    const response = await fetch("config.json?ts=" + Date.now());
    config = await response.json();
}

function updateWatermark() {
    const watermarkDiv = document.getElementById("watermark");
    const textSpan = document.getElementById("watermark-text");
    const qrImg = document.getElementById("watermark-qr");

    if (config.watermarkText || config.watermarkQR) {
        watermarkDiv.style.display = "flex";

        if (config.watermarkText) {
            textSpan.textContent = config.watermarkText + "\nhttps://tally.so/r/" + config.tally_form_id;
        }
        if (config.watermarkQR) {
            qrImg.src = config.watermarkQR;
        }
    } else {
        watermarkDiv.style.display = "none";
    }
}

function updateNoImagesMessage() {
    const message = document.getElementById("no-images");
    const slideshow = document.getElementById("slideshow");

    if (images.length === 0) {
        message.style.display = "block";
        slideshow.style.display = "none";
    } else {
        message.style.display = "none";
        slideshow.style.display = "block";
    }
}

async function fetchImages() {
    try {
        updating = true;
        const response = await fetch(config.imageList + "?ts=" + Date.now());
        const newImages = await response.json();

        if (JSON.stringify(newImages) !== JSON.stringify(images)) {
            images = newImages;
            current = 0;
            console.log("Images mises à jour :", images);
        }

        updateNoImagesMessage();
    } catch (e) {
        console.error("Erreur lors du chargement des images :", e);
    } finally {
        updating = false;
    }
}

function showNextImage() {
    if (images.length > 0 && !updating) {
        const img = document.getElementById("slideshow");
        img.src = images[current];
        current = (current + 1) % images.length;
    }
}

async function startSlideshow() {
    await loadConfig();
    await fetchImages();
    updateWatermark();
    showNextImage();

    setInterval(showNextImage, config.intervalSlideshow);
    setInterval(fetchImages, config.intervalRefresh);
}

startSlideshow();