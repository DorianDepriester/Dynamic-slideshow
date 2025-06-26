let config = {};
let images = []; // tableau de [chemin, auteur]
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
    const authorLabel = document.getElementById("author");

    const hasImages = images.length > 0;
    message.style.display = hasImages ? "none" : "block";
    slideshow.style.display = hasImages ? "block" : "none";
    authorLabel.style.display = hasImages ? "block" : "none";
}

async function fetchImages() {
    try {
        updating = true;
        const response = await fetch(config.imageList + "?ts=" + Date.now());
        const imageDict = await response.json();

        const newImages = Object.entries(imageDict); // transforme {chemin: auteur} en [[chemin, auteur], ...]

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
        const [path, author] = images[current];
        const img = document.getElementById("slideshow");
        const label = document.getElementById("author");

        img.src = path;
        label.textContent = author || "";
        label.style.display = "block";

        current = (current + 1) % images.length;
    }
}

async function startSlideshow() {
    await loadConfig();
    await fetchImages();
    updateWatermark();
    showNextImage();

    setInterval(showNextImage, config.intervalSlideshow * 1000);
    setInterval(fetchImages, config.intervalRefresh * 100);
}

startSlideshow();
