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
        <input type="button" class="req-send" value="Visualize This"></input>
      </div>
    </div>

    <div class="right-side">
      <div id="response" class="response-area"></div>
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
    responseArea.innerHTML = "<p>Please enter a request in the left textarea.</p>";
    return;
  }

  responseArea.innerHTML = "<p>Processing...</p>";

  try {
    const response = await fetch("http://localhost:8000/api/generate-response", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ userContent: inputContent }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch response from server.");
    }

    const data = await response.json();

    // Extract content between triple backticks
    const responseText = data.generatedResponse;
    const codeBlockMatch = responseText.match(/```([\s\S]*?)```/); // Regex to find text between ```
    const explanation = responseText.replace(/```[\s\S]*?```/, "").trim(); // Remove code block

    if (codeBlockMatch) {
      const codeContent = codeBlockMatch[1]; // Get the content inside ```
      // Render the code block and explanation
      responseArea.innerHTML = `
        <pre><code>${codeContent}</code></pre>
        <p>${explanation}</p>
      `;
    } else {
      responseArea.innerHTML = `<p>${responseText}</p>`;
    }
  } catch (error) {
    responseArea.innerHTML = `<p>Error: ${error.message}</p>`;
  }
}

}

