// script.js content

document.addEventListener("DOMContentLoaded", function () {
    // Add event listener to all h2 elements (titles of each section)
    document.querySelectorAll('h2').forEach(function (title) {
        title.addEventListener('click', function () {
            const sectionContent = this.nextElementSibling;
            if (sectionContent.style.display === 'none' || sectionContent.style.display === '') {
                sectionContent.style.display = 'block';
            } else {
                sectionContent.style.display = 'none';
            }
        });
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');


var messageQueue = [];

function sendMessage() {
    var userMessage = $('#inputMessage').val().trim();
    if (!userMessage) {
        return;
    }
    $('#inputMessage').val(''); // Clear the input field
    $('#messages').append(`<div class="message user-message"><p>User: ${userMessage}</p></div>`);

    // Add the message and a placeholder for the bot's response to the message queue
    var messageId = 'message' + new Date().getTime();
    messageQueue.push({ id: messageId, userMessage: userMessage, botResponse: null });
    $('#messages').append(`<div class="message bot-message" id="${messageId}"><p>Bot: ...</p></div>`);

    // Disable the send button
    $('#sendMessageButton').prop('disabled', true);

    $.ajax({
        url: '/ask/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: userMessage }),
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            var botResponse = data.response;

            // Find the corresponding message in the queue and update its botResponse
            for (var i = 0; i < messageQueue.length; i++) {
                if (messageQueue[i].userMessage === userMessage) {
                    messageQueue[i].botResponse = botResponse;
                    break;
                }
            }

            // Display the messages in order
            for (var i = 0; i < messageQueue.length; i++) {
                var message = messageQueue[i];
                if (message.botResponse !== null) {
                    $('#' + message.id).html(`<p>Bot: ${message.botResponse}</p>`);
                } else {
                    break;
                }
            }

            // Enable the send button
            $('#sendMessageButton').prop('disabled', false);

            // Scroll to the end of the messages
            var messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        },
        error: function (xhr, status, error) {
            if (xhr.status === 429) {
                $('#inputMessage').val('Too many requests. Please wait a minute.');

                // Disable the send button
                $('#sendMessageButton').prop('disabled', true);

                // Clear the message and enable the button after 1 minute
                setTimeout(function () {
                    $('#inputMessage').val('');
                    $('#sendMessageButton').prop('disabled', false);
                }, 60000);
            } else {
                console.log('An error occurred:', error);

                // Enable the send button
                $('#sendMessageButton').prop('disabled', false);
            }

            // Remove the "..." message
            $('#' + messageId).remove();
        }
    });
}







function appendMessage(message, sender) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender);

    // Add a line break after the user message
    messageDiv.innerHTML = `<div class="message bot-message"><p>${message}</p></div>`;

    messagesDiv.appendChild(messageDiv);

    // Scroll to the end of the messages div
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

$(document).ready(function () {
    $("a").on('click', function (event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800, function () {
                window.location.hash = hash;
            });
        }
    });
});

function toggleMenu() {
    const menu = document.querySelector(".menu-links");
    const icon = document.querySelector(".hamburger-icon");
    menu.classList.toggle("open");
    icon.classList.toggle("open");
}