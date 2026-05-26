// INTERACTIVE OUTFIT RECOMMENDATION DEMO
// Displays three uploaded clothing images as a suggested outfit combination.

const clothingUpload = document.getElementById("clothingUpload");
const occasion = document.getElementById("occasion");
const generateBtn = document.getElementById("generateBtn");
const recommendationSection = document.getElementById("recommendationSection");
const selectedOccasion = document.getElementById("selectedOccasion");

const topImage = document.getElementById("topImage");
const bottomImage = document.getElementById("bottomImage");
const shoesImage = document.getElementById("shoesImage");

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