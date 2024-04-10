document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.getElementById("chatBox");
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");

    sendButton.addEventListener("click", function() {
        const userMessage = userInput.value;
        
        // Append user message to chat box
        appendMessage("You", userMessage, "user");

        // Here, you can send the user message to your chatbot API for processing
        // and get the chatbot's response
        
        // For demonstration purposes, let's simulate a chatbot response
        const chatbotResponse = "Hello, how can I assist you?";
        
        // Append chatbot response to chat box
        appendMessage("Chatbot", chatbotResponse, "chatbot");

        // Clear user input
        userInput.value = "";
    });

    function appendMessage(sender, message, type) {
        const messageElement = document.createElement("div");
        messageElement.className = type;
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(messageElement);

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});