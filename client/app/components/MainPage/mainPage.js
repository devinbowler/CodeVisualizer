import { base } from "../../main/base.js";
import { viewManager } from "../../main/viewManager.js";

export class mainPage extends base {
  #container = null;

  constructor() {
    super();
    this.loadCSS("mainPage");
  }

  render() {
    this.#container = document.createElement("div");
    this.#container.classList.add("main-container");
    this.#container.innerHTML = `
      <div class="left-side">
        <div class="submit-req">
          <textarea id="content" placeholder="Enter request here..."></textarea>
          <input type="button" class="req-send" value="Send"></input>
        </div>
      </div>

      <div class="right-side">
        <textarea id="response" placeholder="Response will be here..." readonly></textarea>
      </div>
    `;

    // Attach event listener for the Send button
    this.#container.querySelector(".req-send").addEventListener("click", this.#sendRequest.bind(this));

    return this.#container;
  }

  async #sendRequest() {
    const inputContent = document.getElementById("content").value;
    const responseArea = document.getElementById("response");

    if (!inputContent.trim()) {
      responseArea.value = "Please enter a request in the left textarea.";
      return;
    }

    responseArea.value = "Processing...";

    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer YOUR_OPENAI_API_KEY`, // Replace with your actual API key
        },
        body: JSON.stringify({
          model: "gpt-4o",
          messages: [
            {
              role: "system",
              content: (
                "You are an AI that only responds with large, detailed ASCII visuals followed by a concise, clear explanation. "
                + "Do not provide any context, description, or introductory text before the ASCII visual. The ASCII visual must be large, well-structured, "
                + "and as detailed as possible. Use clear spacing, alignment, and shapes to make the visual precise and intuitive. "
                + "After the ASCII visual, you must provide a concise explanation (no more than 2 paragraphs) that explains the concept illustrated by the ASCII. "
                + "The explanation must be clear and informative, and must never come before the visual."
              ),
            },
            {
              role: "user",
              content: inputContent,
            },
          ],
          temperature: 0.9,
          max_tokens: 2000,
          n: 1,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch response from OpenAI.");
      }

      const data = await response.json();
      responseArea.value = data.choices[0].message.content;
    } catch (error) {
      responseArea.value = `Error: ${error.message}`;
    }
  }
}

