const sidebar = document.querySelector("#sidebar");
const hide_sidebar = document.querySelector(".hide-sidebar");
const new_chat_button = document.querySelector(".new-chat");

hide_sidebar.addEventListener( "click", function() {
    sidebar.classList.toggle( "hidden" );
} );

const user_menu = document.querySelector(".user-menu ul");
const show_user_menu = document.querySelector(".user-menu button");

show_user_menu.addEventListener( "click", function() {
    if( user_menu.classList.contains("show") ) {
        user_menu.classList.toggle( "show" );
        setTimeout( function() {
            user_menu.classList.toggle( "show-animate" );
        }, 200 );
    } else {
        user_menu.classList.toggle( "show-animate" );
        setTimeout( function() {
            user_menu.classList.toggle( "show" );
        }, 50 );
    }
} );

const models = document.querySelectorAll(".model-selector button");

for( const model of models ) {
    model.addEventListener("click", function() {
        document.querySelector(".model-selector button.selected")?.classList.remove("selected");
        model.classList.add("selected");
    });
}

const message_box = document.querySelector("#message");

message_box.addEventListener("keyup", function() {
    message_box.style.height = "auto";
    let height = message_box.scrollHeight + 2;
    if( height > 200 ) {
        height = 200;
    }
    message_box.style.height = height + "px";
});

function show_view( view_selector ) {
    document.querySelectorAll(".view").forEach(view => {
        view.style.display = "none";
    });

    document.querySelector(view_selector).style.display = "flex";
}

new_chat_button.addEventListener("click", function() {
    show_view( ".new-chat-view" );
    document.querySelectorAll(".conversations li").forEach(li => {
        li.classList.remove("active");
    });
});

document.querySelectorAll(".conversation-button").forEach(button => {
    button.addEventListener("click", function() {
        // Remove the "active" class from all list items
        document.querySelectorAll(".conversations li").forEach(li => {
            li.classList.remove("active");
        });

        // Add the "active" class to the parent list item of the clicked button
        button.closest("li").classList.add("active");

        // Check the button text to determine which view to show
        if (button.textContent.includes("Current Conversation..")) {
            show_view(".current-conversation-view");
        } else {
            show_view(".conversation-view");
        }
    });
});



document.addEventListener("DOMContentLoaded", function() {
    show_view(".new-chat-view");
    document.querySelectorAll(".conversations li").forEach(li => {
        li.classList.remove("active");
    });
});

document.querySelector('.send-button').addEventListener('click', async function() {
    show_view('.current-conversation-view');
    
    const messageInput = document.querySelector('#message');
    const messageText = messageInput.value.trim();
    
    if (messageText) {
        const conversation = document.querySelector('.current-conversation-view');
        
        // Create a container div for the user message
        const userMessage = document.createElement('div');
        userMessage.classList.add('user', 'message');
        
        // Create the identity div and add the user icon
        const identity = document.createElement('div');
        identity.classList.add('identity');
        
        const userIcon = document.createElement('i');
        userIcon.classList.add('user-icon');
        userIcon.textContent = 'u';  // Customize this with the user's avatar or icon
        
        identity.appendChild(userIcon);
        
        // Add the identity div to the user message
        userMessage.appendChild(identity);
        
        // Create the content div and add the message text
        const content = document.createElement('div');
        content.classList.add('content');
        
        const messageParagraph = document.createElement('p');
        messageParagraph.textContent = messageText;
        
        content.appendChild(messageParagraph);
        
        // Add the content div to the user message
        userMessage.appendChild(content);
        
        // Append the user message to the conversation
        conversation.appendChild(userMessage);
        
        // Clear the input field
        messageInput.value = '';
        
        // Disable the input field while waiting for a response
        messageInput.disabled = true;
        
        // Scroll the conversation view to the bottom
        conversation.scrollTop = conversation.scrollHeight;
        
        // Display a temporary message indicating a response is being processed
        const tempMessage = document.createElement('div');
        tempMessage.classList.add('assistant', 'message');
        
        const tempIdentity = document.createElement('div');
        tempIdentity.classList.add('identity');
        
        const tempIcon = document.createElement('i');
        tempIcon.classList.add('gpt', 'user-icon');
        tempIcon.textContent = 'G';
        
        tempIdentity.appendChild(tempIcon);
        tempMessage.appendChild(tempIdentity);
        
        const tempContent = document.createElement('div');
        tempContent.classList.add('content');
        
        const tempParagraph = document.createElement('p');
        tempParagraph.textContent = 'Analysing your answer...';
        
        tempContent.appendChild(tempParagraph);
        tempMessage.appendChild(tempContent);
        
        // Append the temporary message to the conversation
        conversation.appendChild(tempMessage);
        
        // Scroll the conversation view to the bottom
        conversation.scrollTop = conversation.scrollHeight;
        
        // Get the response asynchronously from the GPT function
        const answer = await getResponse(messageText);
        
        // Remove the temporary message
        conversation.removeChild(tempMessage);
        
        // Create a container div for the assistant message
        const assistantMessage = document.createElement('div');
        assistantMessage.classList.add('assistant', 'message');
        
        // Create the identity div and add the assistant icon
        const assistantIdentity = document.createElement('div');
        assistantIdentity.classList.add('identity');
        
        const assistantIcon = document.createElement('i');
        assistantIcon.classList.add('gpt', 'user-icon');
        assistantIcon.textContent = 'G';
        
        assistantIdentity.appendChild(assistantIcon);
        assistantMessage.appendChild(assistantIdentity);
        
        // Create the content div and add the response text
        const assistantContent = document.createElement('div');
        assistantContent.classList.add('content');
        
        const responseParagraph = document.createElement('p');
        responseParagraph.textContent = answer;
        
        assistantContent.appendChild(responseParagraph);
        assistantMessage.appendChild(assistantContent);
        
        // Append the assistant message to the conversation
        conversation.appendChild(assistantMessage);
        
        // Scroll the conversation view to the bottom
        conversation.scrollTop = conversation.scrollHeight;
        
        // Re-enable the input field for new messages
        messageInput.disabled = false;
    }
});

async function getResponse(messageText) {
    // Define the API endpoint
    const apiEndpoint = '/converse';

    // Determine if this is the first message
    const conversation = document.querySelector('.current-conversation-view');
    const isFirstMessage = conversation.querySelectorAll('.user.message').length === 1;

    // Prepare the request body
    let requestBody = {};
    if (isFirstMessage) {
        requestBody.is_first_message = true;
    } else {
        requestBody.user_response = messageText;
    }

    // Use fetch API to send a POST request to the endpoint
    try {
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        // Check if the response is successful
        if (response.ok) {
            // Parse the JSON response
            const jsonResponse = await response.json();
            
            // Check if the response contains an error
            if (jsonResponse.status === 'success') {
                // Return the response message from the server
                return jsonResponse.response;
            } else {
                console.error('Error in response:', jsonResponse.error);
                return `Error: ${jsonResponse.error}`;
            }
        } else {
            console.error('Interview completed, All the best!');
            return 'Interview completed, All the best!';
        }
    } catch (error) {
        console.error('Fetch error:', error);
        return 'Error: An error occurred while fetching the response';
    }
}
