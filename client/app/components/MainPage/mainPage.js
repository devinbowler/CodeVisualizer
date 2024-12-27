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
          responseArea.innerHTML = "<p>Please enter what you want visualized in the left textarea.</p>";
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
              body: JSON.stringify({ textInput: inputContent }),
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

              // Poll for the GIF until it's available
              try {
                  const gifAvailable = await this.#pollForGIF(gifUrl);
                  if (gifAvailable) {
                      responseArea.innerHTML = `
                          <img 
                              src="${gifUrl}" 
                              alt="Rendered GIF" 
                              style="max-width: 80%; display: block;" />
                      `;
                  }
              } catch (error) {
                  responseArea.innerHTML = `<p>Error: ${error.message}</p>`;
              }
          }
      } catch (error) {
          responseArea.innerHTML = `<p>Error: ${error.message}</p>`;
      }
  }

  #pollForGIF(gifUrl, retries = 10, delay = 2000) {
      return new Promise(async (resolve, reject) => {
          for (let i = 0; i < retries; i++) {
              try {
                  const gifResponse = await fetch(gifUrl, { method: "GET" });
                  if (gifResponse.ok) {
                      resolve(true); // GIF is ready
                      return;
                  }
              } catch (err) {
                  console.error(`Retrying... (${i + 1}/${retries})`);
              }
              await new Promise((resolve) => setTimeout(resolve, delay)); // Wait before retrying
          }
          reject(new Error("Failed to fetch the generated GIF after multiple retries."));
      });
  }

}

