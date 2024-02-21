/**
 * Disables scrolling on the body element.
 */
function disableScroll() {
	document.body.style.overflow = "hidden";
}
/**
 * Enables scrolling on the body element.
 */
function enableScroll() {
	document.body.style.overflow = "";
}
/**
 * Opens a window by fetching content from the specified URL and displaying 
 * it in a modal.
 * @param {Event} event - The click event that triggered the function.
 * @returns {Promise<undefined>} - A Promise that resolves when the window
 *  is opened.
 */
async function openWindow(event) {
	event.preventDefault();

	const response = await fetch(event.target.getAttribute("href"));

	if (!response.ok) {
		throw new Error("Failed to fetch.");
	}

	const content = await response.text();
	const element = document.getElementById("readPost");

	element.innerHTML = content;
	element.style.display = "flex";

	disableScroll();
	addEventToClose();
}
/**
 * Adds a click event listener to all elements with the "reading" class,
 * to open the window when clicked.
 */
function addEventToReadPost() {
	const readingLinks = document.querySelectorAll("a.reading");
	readingLinks.forEach(link => link.addEventListener("click", openWindow));
}
/**
 * Closes the window and restores scrolling on the body element.
 * @param {Event} event - The click event that triggered the function.
 * @returns {undefined}
 */
function closeWindow(event) {
	try {
		event.preventDefault();

		const element = document.getElementById("readPost");

		element.style.display = "none";
		element.innerHTML = "";

		enableScroll();
		addEventToReadPost();
	} catch (error) {
		throw new Error(error);
	}
}
/**
 * Adds a click event listener to the close button,
 * to close the window when clicked.
 * @returns {undefined}
 */
function addEventToClose() {
	document.getElementById("close").addEventListener("click", closeWindow);
}

document.addEventListener("DOMContentLoaded", addEventToReadPost);
