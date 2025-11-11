// app.js

// Define the backend URL at the top
const backendUrl = "https://assessment-recommendation-system-vg9h.onrender.com";

// Get references to your HTML elements
const queryInput = document.getElementById("query"); // Your text input field
const searchButton = document.getElementById("go");   // Your search button
const resultsContainer = document.getElementById("results"); // A div where results will be displayed

// Add an event listener to the search button
searchButton.addEventListener("click", async () => {
    // 1. Get the current text from the input box when the button is clicked.
    const userQuery = queryInput.value;

    // Optional: Basic validation to make sure the query isn't empty.
    if (!userQuery.trim()) {
        alert("Please enter a search query.");
        return;
    }
    
    // Show a "loading..." message
    resultsContainer.innerHTML = `<p>Searching for recommendations...</p>`;

    try {
        // 2. Use the 'userQuery' variable in the body of your request.
        // This is where you replace the placeholder.
        const response = await fetch(`${backendUrl}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: userQuery }) // Using the real user query here
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "An error occurred on the server.");
        }

        const data = await response.json();
        displayResults(data.recommended_assessments);

    } catch (error) {
        console.error("Failed to fetch:", error);
        resultsContainer.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
});

// A function to render the results on the page
function displayResults(assessments) {
    if (!assessments || assessments.length === 0) {
        resultsContainer.innerHTML = `<p>No recommendations found for your query.</p>`;
        return;
    }

    resultsContainer.innerHTML = ``; // Clear the "loading..." message

    assessments.forEach(assessment => {
        const assessmentCard = document.createElement('div');
        assessmentCard.className = 'assessment-card'; // Add a class for styling in your style.css
        
        assessmentCard.innerHTML = `
            <h2><a href="${assessment.url}" target="_blank">${assessment.name}</a></h2>
            <p>${assessment.description}</p>
            <p><strong>Duration:</strong> ${assessment.duration} minutes</p>
            <p><strong>Test Type:</strong> ${assessment.test_type.join(', ')}</p>
        `;
        
        resultsContainer.appendChild(assessmentCard);
  });
}
