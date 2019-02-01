const globals = {}

// called by template on page load
function initialize(pspReference, serverRoot) {

	// get variables from template
	globals.pspReference = pspReference;
	globals.serverRoot = serverRoot;

	// get search results from DB
	$.ajax({
		url: "https://roodvibes.com/" + globals.serverRoot + "/notifications/search/" + globals.pspReference,
		success: data => {
			// handle returned notifications
			let results = sanitizeJSON(data).reverse();

			for (let notification of results) {
				addToDom(notification);
			}
		}
	});
}

// fix stray apostrophes in JSON data
// and return formatted JSON object
function sanitizeJSON(rawText) {
	formattedText = rawText.replace(/"/g, "").replace(/'/g, '"');
	return JSON.parse(formattedText);
}

// add a notification to the DOM and activate code highlighting
// if first = true adds to top
function addToDom(notification) {

	// create elements to be added
	var wrapper = createCollapsibleWrapper(notification);
	var notificationContainer = document.createElement("pre");
	var notificationElement = document.createElement("code");

	// attach to each other
	notificationContainer.appendChild(notificationElement);
	wrapper.appendChild(notificationContainer);

	// set up new element
	notificationElement.classList.add("json");
	notificationElement.innerHTML = JSON.stringify(notification, null, 4);
	notificationContainer.classList.add("hidden");

	// add to DOM
	eventList = document.getElementById("list");
	eventList.appendChild(wrapper);

	// activate highlighting
	hljs.highlightBlock(notificationElement);
}

// create a collapsible div with a summary to hold notifications
function createCollapsibleWrapper(notification) {
	var wrapper = document.createElement("div");
	wrapper.classList.add("collapsible-div");
	wrapper.addEventListener("click", event => event.srcElement.children[0].classList.toggle("hidden"));

	var formattedDate = notification.eventDate.replace(/T/g, " @ ").substring(0, notification.eventDate.length - 7);
	wrapper.innerHTML = notification.eventCode + " | success: " + notification.success + " | " + formattedDate;

	return wrapper;
}

// processes notifications received from server
function receiveNotification(notificationData) {

	// get data from event and json encode
	notification = sanitizeJSON(notificationData);

	// if the event sent by the server is newer, add it to the page
	if (notification.pspReference != lastEventId) {

		// add to DOM
		addToDom(notification, true);

		// update current timestamp
		lastEventId = notification.pspRefernce;
	}

}
