// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {

  const form = document.querySelector('form');
  
  // Add event listener for form submission
  form.addEventListener('submit', function(event) {
      // Prevent the form from actually submitting (for demonstration purposes)
      event.preventDefault();

      // Get form input values
      const name = document.getElementById('username').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      
      // Basic validation for empty fields
      if (!name || !email || !password) {
          alert("All fields are required!");
          return;
      }

      // Simulate form submission success
      alert("Signup Successfully!!");

      // Optionally clear the form after submission
      form.reset();
  });

  // Optional: Enable simple client-side validation (for email format)
  document.getElementById('email').addEventListener('input', function() {
      const email = this.value;
      const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      const emailErrorMessage = document.getElementById('email-error');

      if (!emailPattern.test(email)) {
          if (!emailErrorMessage) {
              const errorMessage = document.createElement('p');
              errorMessage.id = 'email-error';
              errorMessage.style.color = 'red';
              errorMessage.textContent = 'Please enter a valid email address.';
              form.appendChild(errorMessage);
          }
      } else {
          const existingErrorMessage = document.getElementById('email-error');
          if (existingErrorMessage) {
              existingErrorMessage.remove();
          }
      }
  });

});
