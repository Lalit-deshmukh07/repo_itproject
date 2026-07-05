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

if (generateBtn) {
  generateBtn.addEventListener("click", function () {
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
  });
}

const outfitButtons = document.querySelectorAll('.outfit-card button');
outfitButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const card = button.closest('.outfit-card');
    const heading = card?.querySelector('h3');
    const title = heading?.textContent || 'Selected outfit';

    if (selectedOccasion) {
      selectedOccasion.textContent = title;
    }

    if (recommendationSection) {
      recommendationSection.hidden = false;
      recommendationSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
});