// INTERACTIVE OUTFIT RECOMMENDATION DEMO
// Builds a frontend wardrobe and recommends an outfit from selected categories.

const clothingUpload = document.getElementById("clothingUpload");
const cameraUpload = document.getElementById("cameraUpload");
const occasion = document.getElementById("occasion");
const weather = document.getElementById("weather");
const stylePreference = document.getElementById("stylePreference");
const generateBtn = document.getElementById("generateBtn");
const recommendationSection = document.getElementById("recommendations");
const selectedOccasion = document.getElementById("selectedOccasion");
const selectedWeather = document.getElementById("selectedWeather");
const selectedStyle = document.getElementById("selectedStyle");
const aiNote = document.getElementById("aiNote");
const wardrobePanel = document.getElementById("wardrobePanel");
const wardrobeGrid = document.getElementById("wardrobeGrid");
const wardrobeCount = document.getElementById("wardrobeCount");

const topImage = document.getElementById("topImage");
const bottomImage = document.getElementById("bottomImage");
const shoesImage = document.getElementById("shoesImage");

const openLoginBtn = document.getElementById("openLoginBtn");
const loginModal = document.getElementById("loginModal");
const closeLoginBtn = document.getElementById("closeLoginBtn");
const closeLoginBackdrop = document.getElementById("closeLoginBackdrop");
const saveOutfitBtn = document.getElementById("saveOutfitBtn");
const generateAnotherBtn = document.getElementById("generateAnotherBtn");

const wardrobeItems = [];
const categoryOptions = ["Top", "Bottom", "Shoes", "Jacket", "Accessory"];

function openLoginModal() {
  loginModal.hidden = false;
}

function closeLoginModal() {
  loginModal.hidden = true;
}

function guessCategory(index) {
  return categoryOptions[index % categoryOptions.length];
}

function getItemsByCategory(category) {
  return wardrobeItems.filter(function (item) {
    return item.category === category;
  });
}

function chooseItem(category) {
  const matchingItems = getItemsByCategory(category);

  if (matchingItems.length === 0) {
    return null;
  }

  const randomIndex = Math.floor(Math.random() * matchingItems.length);
  return matchingItems[randomIndex];
}

function updateWardrobeCount() {
  const itemLabel = wardrobeItems.length === 1 ? "item" : "items";
  wardrobeCount.textContent = wardrobeItems.length + " " + itemLabel;
}

function renderWardrobeGrid() {
  wardrobeGrid.innerHTML = "";
  wardrobePanel.hidden = wardrobeItems.length === 0;
  updateWardrobeCount();

  wardrobeItems.forEach(function (item) {
    const card = document.createElement("article");
    card.className = "wardrobe-card";

    const image = document.createElement("img");
    image.src = item.imageUrl;
    image.alt = item.name;

    const details = document.createElement("div");
    details.className = "wardrobe-card-details";

    const name = document.createElement("p");
    name.textContent = item.name;

    const select = document.createElement("select");
    select.setAttribute("aria-label", "Category for " + item.name);

    categoryOptions.forEach(function (category) {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      option.selected = item.category === category;
      select.appendChild(option);
    });

    select.addEventListener("change", function () {
      item.category = select.value;
    });

    details.appendChild(name);
    details.appendChild(select);
    card.appendChild(image);
    card.appendChild(details);
    wardrobeGrid.appendChild(card);
  });
}

function addFilesToWardrobe(files) {
  Array.from(files).forEach(function (file) {
    if (!file.type.startsWith("image/")) {
      return;
    }

    const item = {
      id: crypto.randomUUID ? crypto.randomUUID() : Date.now() + "-" + wardrobeItems.length,
      name: file.name || "Camera photo",
      imageUrl: URL.createObjectURL(file),
      category: guessCategory(wardrobeItems.length)
    };

    wardrobeItems.push(item);
  });

  renderWardrobeGrid();
}

function validateRecommendationInputs() {
  if (wardrobeItems.length < 3) {
    alert("Please upload wardrobe images first. You need at least a top, bottom, and shoes.");
    return false;
  }

  if (occasion.value === "") {
    alert("Please select an occasion.");
    return false;
  }

  if (weather.value === "") {
    alert("Please select the weather.");
    return false;
  }

  if (stylePreference.value === "") {
    alert("Please select a style preference.");
    return false;
  }

  if (!chooseItem("Top") || !chooseItem("Bottom") || !chooseItem("Shoes")) {
    alert("Please make sure your wardrobe has at least one Top, one Bottom, and one Shoes item.");
    return false;
  }

  return true;
}

function buildAiNote(extraItem) {
  let note = "This demo selected a top, bottom, and shoes from your wardrobe for " +
    occasion.value.toLowerCase() + " styling in " + weather.value.toLowerCase() +
    " weather with a " + stylePreference.value.toLowerCase() + " preference.";

  if (extraItem) {
    note += " It also recommends adding a jacket because the weather may need an extra layer.";
  }

  return note;
}

function showRecommendedOutfit() {
  if (!validateRecommendationInputs()) {
    return;
  }

  const selectedTop = chooseItem("Top");
  const selectedBottom = chooseItem("Bottom");
  const selectedShoes = chooseItem("Shoes");
  const selectedJacket = ["Cold", "Rainy", "Cloudy"].includes(weather.value) ? chooseItem("Jacket") : null;

  topImage.src = selectedTop.imageUrl;
  bottomImage.src = selectedBottom.imageUrl;
  shoesImage.src = selectedShoes.imageUrl;

  selectedOccasion.textContent = occasion.value;
  selectedWeather.textContent = weather.value;
  selectedStyle.textContent = stylePreference.value;
  aiNote.textContent = buildAiNote(selectedJacket);
  recommendationSection.hidden = false;
  recommendationSection.scrollIntoView({ behavior: "smooth" });
}

clothingUpload.addEventListener("change", function () {
  addFilesToWardrobe(clothingUpload.files);
  clothingUpload.value = "";
});

cameraUpload.addEventListener("change", function () {
  addFilesToWardrobe(cameraUpload.files);
  cameraUpload.value = "";
});

generateBtn.addEventListener("click", showRecommendedOutfit);
generateAnotherBtn.addEventListener("click", showRecommendedOutfit);

saveOutfitBtn.addEventListener("click", function () {
  alert("Outfit saved for demo. Backend save functionality will be added later.");
});

openLoginBtn.addEventListener("click", openLoginModal);
closeLoginBtn.addEventListener("click", closeLoginModal);
closeLoginBackdrop.addEventListener("click", closeLoginModal);

document.addEventListener("keydown", function (event) {
  if (event.key === "Escape" && !loginModal.hidden) {
    closeLoginModal();
  }
});
