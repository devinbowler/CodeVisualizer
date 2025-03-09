import { base } from "../main/base.js";

export class loginPage extends base {
  #container = null;

  constructor() {
    super();
    this.loadCSS("loginPage");
  }



  async #loginUser(username, password) {
    try {
      const response = await fetch("https://loginservice-backend.onrender.com/loginUser", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }), // Send data as JSON
      });

      const result = await response.json(); // Parse JSON response

      if (response.ok && result.success) {
        alert("Logged in successfully!");
      } else {
        alert(result.message || "Invalid credentials!");
      }
    } catch (error) {
      console.error("Error during login:", error);
      alert("An error occurred. Please try again.");
    }
  }

  async #registerUser(username, password) {
    try {
      const response = await fetch("https://loginservice-backend.onrender.com/registerUser", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }), // Send data as JSON
      });

      const result = await response.json(); // Parse JSON response

      if (response.ok && result.success) {
        alert("Account created successfully!");
      } else {
        alert(result.message || "Invalid credentials!");
      }
    } catch (error) {
      console.error("Error during registration:", error);
      alert("An error occurred. Please try again.");
    }
  }







  render() {
    this.#container = document.createElement("div");
    this.#container.classList.add("main-container");
    this.#container.innerHTML = `
      <div class="form-container">
        <div id="login-form" class="form">
          <h2>Login</h2>
          <input type="text" placeholder="Username" id="log-username" />
          <input type="password" placeholder="Password" id="log-password" />
          <button id="login-btn">Login</button>
          <p class="toggle-text">
            Not already a user? <span id="show-register">Make an account.</span>
          </p>
        </div>

        <div id="register-form" class="form hidden">
          <h2>Register</h2>
          <input type="text" placeholder="Username" id="reg-username" />
          <input type="password" placeholder="Password" id="reg-password" />
          <button id="register-btn">Register</button>
          <p class="toggle-text">
            Already a user? <span id="show-login">Login now.</span>
          </p>
        </div>
      </div>
    `;

    this.#addEventListeners();

    return this.#container;
  }



  #addEventListeners() {
    const loginForm = this.#container.querySelector("#login-form");
    const registerForm = this.#container.querySelector("#register-form");
    const showRegister = this.#container.querySelector("#show-register");
    const showLogin = this.#container.querySelector("#show-login");

    const loginSubmit = this.#container.querySelector("#login-btn");
    const registerSubmit = this.#container.querySelector("#register-btn");


    showRegister.addEventListener("click", () => {
      loginForm.classList.add("hidden");
      registerForm.classList.remove("hidden");
    });

    showLogin.addEventListener("click", () => {
      registerForm.classList.add("hidden");
      loginForm.classList.remove("hidden");
    });

    loginSubmit.addEventListener("click", (e) => {
      e.preventDefault(); // Prevent default form submission behavior

      const username = this.#container.querySelector("#log-username").value;
      const password = this.#container.querySelector("#log-password").value;

      this.#loginUser(username, password);
    });

    registerSubmit.addEventListener("click", (e) => {
      e.preventDefault(); // Prevent default form submission behavior

      const username = this.#container.querySelector("#reg-username").value;
      const password = this.#container.querySelector("#reg-password").value;

      this.#registerUser(username, password);
    });
  }
}

