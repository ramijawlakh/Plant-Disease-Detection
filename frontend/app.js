document.getElementById("predictForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById("imageInput");
    const confidence = document.getElementById("confidenceInput").value;
    
    formData.append("file", fileInput.files[0]);
    formData.append("confidence_threshold", confidence);
    formData.append("output_dir", "/tmp/output");
    
    const response = await fetch("/predict/", {
        method: "POST",
        body: formData
    });
    
    if (response.ok) {
        const blob = await response.blob();
        document.getElementById("resultImage").src = URL.createObjectURL(blob);
    } else {
        alert("Error predicting image.");
    }
});

document.getElementById("chatForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    const userInput = document.getElementById("chatInput").value;
    if (!userInput.trim()) return; // Prevent empty messages
    
    // Add user message to chat
    addMessageToChat(userInput, 'user');
    
    // Clear input field
    document.getElementById("chatInput").value = "";
    
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_input: userInput })
        });
        
        const data = await response.json();
        // Add bot response to chat
        addMessageToChat(data.response, 'bot');
        
        // Scroll to bottom of chat
        scrollChatToBottom();
    } catch (error) {
        console.error("Error:", error);
        addMessageToChat("Sorry, there was an error processing your request.", 'bot');
    }
});

// Function to add messages to the chat
function addMessageToChat(message, sender) {
    const chatContainer = document.getElementById("chatContainer");
    
    // Create wrapper div for the message
    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("message-wrapper");
    
    // Create the message element
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = message;
    
    // Add message to wrapper
    messageWrapper.appendChild(messageDiv);
    
    // Add wrapper to chat container
    chatContainer.appendChild(messageWrapper);
    
    // Scroll to bottom
    scrollChatToBottom();
}

// Function to scroll chat to bottom
function scrollChatToBottom() {
    const chatContainer = document.getElementById("chatContainer");
    // Force scroll after a slight delay to ensure DOM has updated
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 50);
}