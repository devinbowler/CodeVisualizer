import { viewManager } from './app/main/viewManager.js';

// Get our root container from the HTML file
const mainContainier = document.getElementById('app');

// Create an instance of the main app controller
const ViewManager = viewManager.getInstance();

// Create the 'content' to append to the container.
const mainContent = await ViewManager.render();

// Render the appController and append it to the HTML container
mainContainier.appendChild(mainContent);
