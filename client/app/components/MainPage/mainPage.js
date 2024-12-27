import { base } from "../../main/base.js";

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
          <textarea id="content" placeholder="Enter Manim code here..."></textarea>
          <input type="button" class="req-send" value="Visualize This"></input>
        </div>
      </div>

      <div class="right-side">
        <div id="response" class="response-area">
          <p>Waiting for input...</p>
        </div>
      </div>
    `;

    this.#container
      .querySelector(".req-send")
      .addEventListener("click", this.#sendRequest.bind(this));

    return this.#container;
  }

  async #sendRequest() {
      const inputContent = document.getElementById("content").value;
      const responseArea = document.getElementById("response");

      if (!inputContent.trim()) {
          responseArea.innerHTML = "<p>Please enter Manim code in the left textarea.</p>";
          return;
      }

      responseArea.innerHTML = "<p>Processing... Please wait for the GIF to render.</p>";

      try {
          // Send the POST request
          const response = await fetch("http://localhost:8000/api/generate-video", {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ manimCode: inputContent }),
          });

          if (!response.ok) {
              throw new Error("Failed to fetch response from server.");
          }

          const data = await response.json();

          if (data.error) {
              responseArea.innerHTML = `<p>Error: ${data.error}</p>`;
          } else {
              const gifUrl = data.videoUrl; // Get GIF URL from response
              console.log(`GIF URL: ${gifUrl}`);

              // Trigger a delayed GET request
              setTimeout(async () => {
                  try {
                      const gifResponse = await fetch(gifUrl, { method: "GET" });

                      if (!gifResponse.ok) {
                          throw new Error("Failed to fetch the generated GIF.");
                      }

                      // Render the GIF after a successful GET
                      responseArea.innerHTML = `
                          <img 
                              src="${gifUrl}" 
                              alt="Rendered GIF" 
                              style="max-width: 100%; height: auto; display: block;" />
                      `;
                  } catch (error) {
                      responseArea.innerHTML = `<p>Error: ${error.message}</p>`;
                  }
              }, 10000); // Wait for 500ms before sending GET
          }
      } catch (error) {
          responseArea.innerHTML = `<p>Error: ${error.message}</p>`;
      }
  }



  /*
  Uncomment this function for ASCII rendering functionality:
  
  async #sendAsciiRequest() {
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

      const responseText = data.generatedResponse;
      const codeBlockMatch = responseText.match(/```([\s\S]*?)```/); // Regex to find text between ```
      const explanation = responseText.replace(/```[\s\S]*?```/, "").trim(); // Remove code block

      if (codeBlockMatch) {
        const codeContent = codeBlockMatch[1]; // Get the content inside ```
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
  */
}

