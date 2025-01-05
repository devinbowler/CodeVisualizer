import { loginPage } from '../login/loginpage.js';

export class viewManager {
   #container = null;       // Main container
   #viewContainer = null;   // View-specific container
   #currentView = null;     // Track the currently rendered view
   #views = {};             // Store initialized views
   
   static instance = null;  // Singleton instance

   constructor() {
     // Define all views
     this.#views = {
       login: new loginPage(),
     };

     // Set inital view
     this.#currentView = this.#views.login;
   }

   /**
    * Renders the main container, navigation menu, and the current view.
    */
   async render() {
      // Create the main container if not already created
      if (!this.#container) {
         this.#container = document.createElement('div');
         this.#container.classList.add('view-manager');
      }

      // Render the current view
      this.#container.innerHTML = ''; // Clear previous content
      this.#container.appendChild(this.#currentView.render());

      return this.#container;
   }

   /**
    * Navigate to a specific view.
    * @param {string} viewName - The name of the view to navigate to.
    * @param {Object} params - Additional parameters to pass to the view.
    */
   async navigate(viewName) {
      // Check if the view exists
      if (!this.#views[viewName]) {
        throw new Error(`View "${viewName}" not found.`);
      }

      // Switch to the new view
      this.#currentView = this.#views[viewName];
      // Re-render the view manager with the new view
      this.render();
   }

   static getInstance() {
     if (!viewManager.instance) {
       viewManager.instance = new viewManager();
     }
     return viewManager.instance;
   }
}
