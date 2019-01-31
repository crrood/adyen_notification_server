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
			let results = sanitizeJSON(data);

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

	// create element to be added
	var notificationContainer = document.createElement("pre");
	var notificationElement = document.createElement("code");
	notificationContainer.appendChild(notificationElement);

	// set up new element
	notificationElement.classList.add("json");
	notificationElement.innerHTML = JSON.stringify(notification, null, 4);

	// add to DOM
	eventList = document.getElementById("list");
	eventList.appendChild(notificationContainer);

	// activate highlighting
	hljs.highlightBlock(notificationElement);
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
