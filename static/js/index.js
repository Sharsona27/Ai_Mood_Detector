// Select elements from the DOM
const homeLink = document.getElementById('homeLink');
const homePageContent = document.getElementById('homePageContent');
const additionalContent = document.getElementById('additionalContent');

// Function to show or hide content when "Home" is clicked
homeLink.addEventListener('click', function(event) {
  event.preventDefault(); // Prevent default anchor behavior
  
  // Toggle visibility of the content sections
  homePageContent.style.display = 'block';
  additionalContent.style.display = 'block';
});
