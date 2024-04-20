document.addEventListener("DOMContentLoaded",async function() {
    const chatBox = document.getElementById("chatBox");
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");

    async function postData(url = "", data = {}) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        return response.json();
    }
    let responseData = await postData("/converse", {
        is_first_message: true
    });
    appendMessage("Interviewer", responseData.response, "chatbot");
    sendButton.addEventListener("click",async function() {
        const userMessage = userInput.value;
        
        // Append user message to chat box
        appendMessage("You", userMessage, "user");

        responseData = await postData("/converse", {
            is_first_message: false,
            user_response: userMessage
        });
        
        // Append chatbot response to chat box
        appendMessage("Interviewer", responseData.response, "chatbot");

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