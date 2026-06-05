// INTERACTIVE OUTFIT RECOMMENDATION DEMO
// Displays three uploaded clothing images as a suggested outfit combination.

const clothingUpload = document.getElementById("clothingUpload");
const occasion = document.getElementById("occasion");
const generateBtn = document.getElementById("generateBtn");
const recommendationSection = document.getElementById("recommendations");
const selectedOccasion = document.getElementById("selectedOccasion");

const topImage = document.getElementById("topImage");
const bottomImage = document.getElementById("bottomImage");
const shoesImage = document.getElementById("shoesImage");

const openLoginBtn = document.getElementById("openLoginBtn");
const loginModal = document.getElementById("loginModal");
const closeLoginBtn = document.getElementById("closeLoginBtn");
const closeLoginBackdrop = document.getElementById("closeLoginBackdrop");
const saveOutfitBtn = document.getElementById("saveOutfitBtn");
const generateAnotherBtn = document.getElementById("generateAnotherBtn");

function openLoginModal() {
  loginModal.hidden = false;
}

function closeLoginModal() {
  loginModal.hidden = true;
}

function showRecommendedOutfit() {
  const uploadedFiles = clothingUpload.files;

  if (uploadedFiles.length < 3) {
    alert("Please upload at least 3 clothing images: top, bottom, and shoes.");
    return;
  }

  if (occasion.value === "") {
    alert("Please select an occasion.");
    return;
  }

  topImage.src = URL.createObjectURL(uploadedFiles[0]);
  bottomImage.src = URL.createObjectURL(uploadedFiles[1]);
  shoesImage.src = URL.createObjectURL(uploadedFiles[2]);

  selectedOccasion.textContent = occasion.value;
  recommendationSection.hidden = false;
  recommendationSection.scrollIntoView({ behavior: "smooth" });
}

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
