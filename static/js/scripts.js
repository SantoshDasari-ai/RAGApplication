document.addEventListener("DOMContentLoaded", function () {
  const mainContainer = document.querySelector("main");
  const chatSection = document.getElementById("chatSection");
  const userInput = document.getElementById("userInput");
  const scrollToBottomBtn = document.getElementById("scrollToBottomBtn");
  const sendButton = document.getElementById("sendButton");
  const sideMenu = document.getElementById("sideMenu");
  const toggleMenuBtn = document.getElementById("toggleMenuBtn");
  const sampleQuestions = document.getElementById("sampleQuestions");
  const sampleButtons = document.querySelectorAll(".sample-question-btn");
  const introSection = document.querySelector(".intro-section");

  toggleMenuBtn.addEventListener("click", function () {
    if (sideMenu.style.width === "250px") {
      sideMenu.style.width = "0";
      document.body.classList.remove("menu-open");
    } else {
      sideMenu.style.width = "250px";
      document.body.classList.add("menu-open");
    }
  });

  sampleButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const question = button.getAttribute("data-question");
      userInput.value = question;
      sendMessage();

      introSection.style.display = "none";
      sampleQuestions.style.display = "none";
    });
  });

  function displayMessage(message, isUser) {
    const messageContainer = document.createElement("div");
    messageContainer.className = "message-container";

    const messageDiv = document.createElement("div");
    messageDiv.className = "message";

    if (isUser) {
      messageContainer.classList.add("user-message-container");
      messageDiv.classList.add("user-message");
    } else {
      messageContainer.classList.add("bot-message-container");
      const botIcon = document.createElement("span");
      botIcon.className = "bot-icon";
      botIcon.innerText = "✨";
      messageContainer.appendChild(botIcon);
      messageDiv.classList.add("bot-message");
      if (message === "Thinking...") {
        messageDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
      } else {
        messageDiv.innerHTML = marked.parse(message);
      }
    }

    messageContainer.appendChild(messageDiv);
    chatSection.appendChild(messageContainer);
    scrollToBottom();

    return messageContainer;
  }

  function sendMessage() {
    const message = userInput.value;
    if (message.trim() === "") return;

    displayMessage(message, true);

    const responseContainer = displayMessage("Thinking...", false);

    fetch("/get_answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: message }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.body.getReader();
      })
      .then((reader) => {
        const decoder = new TextDecoder();
        let fullResponse = "";

        function readStream() {
          reader.read().then(({ done, value }) => {
            if (done) {
              scrollToBottom();
              addFeedbackButtons(responseContainer, fullResponse);
              return;
            }
            let chunk = decoder.decode(value, { stream: true });
            let lines = chunk.split("\n\n");
            lines.forEach((line) => {
              if (line.startsWith("data: ")) {
                let data = JSON.parse(line.slice(6));
                if (data.partial_answer) {
                  fullResponse = data.partial_answer;
                  responseContainer.querySelector(".message").innerHTML =
                    marked.parse(fullResponse);
                  scrollToBottom();
                }
                if (data.complete) {
                  if (data.question_count >= 50) {
                    displayMessage(
                      "You have reached the chat limit of this session. Please refresh the page to start a new session.",
                      false
                    );
                  }
                }
              }
            });
            readStream();
          });
        }

        readStream();
      })
      .catch((error) => {
        console.error("Error:", error);
        responseContainer.querySelector(".message").innerHTML =
          "An error occurred. Please try again later.";
        scrollToBottom();
      });

    userInput.value = "";
    autoResize(userInput);
  }

  function addFeedbackButtons(container) {
    const feedbackContainer = document.createElement("div");
    feedbackContainer.className = "feedback-container";

    const thumbsUp = document.createElement("button");
    thumbsUp.className = "thumbs-up";
    thumbsUp.innerHTML = "👍";

    const thumbsDown = document.createElement("button");
    thumbsDown.className = "thumbs-down";
    thumbsDown.innerHTML = "👎";

    const copyButton = document.createElement("button");
    copyButton.className = "copy-button";
    copyButton.innerHTML = "📋"; // Copy icon

    // Tooltip for thumbs up
    thumbsUp.addEventListener("mouseenter", () => {
      showTooltip(thumbsUp, "This was helpful!");
    });

    // Tooltip for thumbs down
    thumbsDown.addEventListener("mouseenter", () => {
      showTooltip(thumbsDown, "Could be improved!");
    });

    // Tooltip for copy button
    copyButton.addEventListener("mouseenter", () => {
      showTooltip(copyButton, "Copy answer");
    });

    // Feedback confirmation
    const showThanksTooltip = (button) => {
      showTooltip(button, "Thanks for your feedback!");
    };

    const highlightButton = (button) => {
      button.style.borderColor = "purple"; // Change border color to purple
      setTimeout(() => {
        button.style.borderColor = ""; // Reset border color after a short delay
      }, 2000); // Adjust the duration as needed
    };

    thumbsUp.addEventListener("click", () => {
      sendFeedback("positive", container);
      highlightButton(thumbsUp);
      showThanksTooltip(thumbsUp);
    });

    thumbsDown.addEventListener("click", () => {
      sendFeedback("negative", container);
      highlightButton(thumbsDown);
      showThanksTooltip(thumbsDown);
    });

    // Copy button functionality
    copyButton.addEventListener("click", () => {
      const answerText = container.querySelector(".message").textContent;
      if (navigator.clipboard) {
        navigator.clipboard
          .writeText(answerText)
          .then(() => {
            showTooltip(copyButton, "Copied to clipboard!");
          })
          .catch((err) => {
            console.error("Could not copy text: ", err);
          });
      } else {
        // Fallback method
        const textarea = document.createElement("textarea");
        textarea.value = answerText;
        document.body.appendChild(textarea);
        textarea.select();
        try {
          document.execCommand("copy");
          showTooltip(copyButton, "Copied to clipboard!");
        } catch (err) {
          console.error("Fallback: Could not copy text: ", err);
        }
        document.body.removeChild(textarea);
      }
    });

    feedbackContainer.appendChild(thumbsUp);
    feedbackContainer.appendChild(thumbsDown);
    feedbackContainer.appendChild(copyButton); // Add copy button to the container
    container.appendChild(feedbackContainer);
  }

  function sendFeedback(feedbackType, container) {
    const question =
      container.previousElementSibling.querySelector(".message").textContent;
    const answer = container.querySelector(".message").textContent;

    fetch("/store_feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question, answer, feedback: feedbackType }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) {
          alert("Failed to store feedback. Please try again.");
        }
      })
      .catch((error) => {
        console.error("Error storing feedback:", error);
        alert("An error occurred while storing feedback.");
      });
  }

  function autoResize(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
  }

  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      if (event.shiftKey) {
        const cursorPosition = userInput.selectionStart;
        userInput.value =
          userInput.value.substring(0, cursorPosition) +
          "\n" +
          userInput.value.substring(cursorPosition);
        userInput.selectionStart = cursorPosition + 1;
        userInput.selectionEnd = cursorPosition + 1;
        event.preventDefault();
        autoResize(userInput);
      } else {
        event.preventDefault();
        sendMessage();
      }
    }
  });

  sendButton.addEventListener("click", sendMessage);

  userInput.addEventListener("input", function () {
    autoResize(userInput);
  });

  mainContainer.addEventListener("scroll", function () {
    if (
      mainContainer.scrollTop <
      mainContainer.scrollHeight - mainContainer.clientHeight - 50
    ) {
      scrollToBottomBtn.classList.add("show");
    } else {
      scrollToBottomBtn.classList.remove("show");
    }
  });

  scrollToBottomBtn.addEventListener("click", scrollToBottom);

  autoResize(userInput);
  scrollToBottom();
});

function scrollToBottom() {
  const mainContainer = document.querySelector("main");
  mainContainer.scrollTop = mainContainer.scrollHeight;
}

function showTooltip(element, message) {
  const tooltip = document.createElement("span");
  tooltip.className = "tooltip";
  tooltip.textContent = message;
  document.body.appendChild(tooltip);
  const rect = element.getBoundingClientRect();
  tooltip.style.left = `${
    rect.left + rect.width / 2 - tooltip.offsetWidth / 2
  }px`;
  tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;

  // Remove tooltip on mouse leave
  const removeTooltip = () => {
    tooltip.remove();
    element.removeEventListener("mouseleave", removeTooltip); // Clean up the event listener
  };

  element.addEventListener("mouseleave", removeTooltip);
}
