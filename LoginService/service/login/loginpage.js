import { base } from "../main/base.js";

export class loginPage extends base {
  #container = null;

  constructor() {
    super();
    this.loadCSS("loginPage");
  }


  render() {
      this.#container = document.createElement("div");
      this.#container.classList.add("main-container");
      this.#container.innerHTML = `
        <div class="login-form">Form</div>
      `;

      return this.#container;
  }
}


