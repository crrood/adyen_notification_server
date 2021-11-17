var lastEventId = 1;
var currentNotificationId = 0;
var notificationsPerRequest = 10;

const globals = {};

// called by html on page load
function initialize(merchant_account, server_root) {

	// load variables from template
	globals.merchant_account = merchant_account;
	globals.server_root = server_root;

	// query server for more notifications
	document.querySelector("#loadMoreBtn").addEventListener("click", () => {

		// calculate range to ask for
		firstNotification = currentNotificationId + 1;
		lastNotification = currentNotificationId + 1 + notificationsPerRequest;
		url = globals.server_root + "/notifications/" + globals.merchant_account + "/" + firstNotification.toString() + "/" + lastNotification.toString();
		currentNotificationId += notificationsPerRequest;

		// add returned notifications to DOM
		var req = new XMLHttpRequest();
		req.onreadystatechange = function(){
			if (this.readyState == 4) {

				// parse response
				let notifications = sanitizeJSON(this.responseText);

				// create DOM element for each JSON object in response
				for (var i = 0; i < notifications.length; i++) {
					addToDom(notifications[i], false);
				}

				// hide the button if there are no more notifications available
				if (notifications.length < notificationsPerRequest) {
					document.querySelector("#loadMoreBtn").style.display = "none";
				}
			}
		}

		// send request
		req.open("GET", url, true);
		req.send();

	});

	// initialize socket connection
	var socket = io.connect("", {
		path: globals.server_root + "/socket.io", 
		reconnection: false
	});

	// get initial notification from server on page load
	socket.on("connect", () => {
		socket.emit("request_latest", 
			{ merchantAccount: globals.merchant_account }, 
			data => { 
				receiveNotification(data);
			}
		);
	});

	// socket event listeners
	socket.on("notification_available", msg => {
		if (msg.merchantAccount == globals.merchant_account) {
			receiveNotification(msg.notificationData);
		}
	});
}

// fix stray apostrophes in JSON data
// convert python booleans to javascript
// and return formatted JSON object
function sanitizeJSON(rawText) {
	formattedText = rawText.replace(/False/g, "false").replace(/True/g, "true");
	formattedText = formattedText.replace(/'{/g, "{").replace(/}'/g, "}");
	formattedText = formattedText.replace(/\\u2019/g, "'").replace(/\\/g, "");
	try {
		return JSON.parse(formattedText);
	}
	catch(e) {
		console.error(e);
		console.log("raw input:");
		console.log(rawText);
		console.log("formatted input:");
		console.log(formattedText);
	}
};

// add a notification to the DOM and activate code highlighting
// if first = true adds to top
function addToDom(notification, first) {

	// create element to be added
	var notificationContainer = document.createElement("pre");
	var notificationElement = document.createElement("code");
	notificationContainer.appendChild(notificationElement);

	// set up new element
	if (first) {
		if (document.querySelector(".first") != null) {
			document.querySelector(".first").classList.remove("first");
		}
		notificationElement.classList.add("first");
	}
	notificationElement.classList.add("json");
	notificationElement.innerHTML = JSON.stringify(notification, null, 4);

	// add to DOM
	eventList = document.getElementById("list");
	if (first) {
		eventList.insertBefore(notificationContainer, eventList.firstChild);
	} else {
		eventList.appendChild(notificationContainer);
	}

	// activate highlighting
	hljs.highlightBlock(notificationElement);
};

// processes notifications received from server
function receiveNotification(notificationData) {

	// get data from event and json encode
	notification = sanitizeJSON(notificationData);

	// add it to the page
	addToDom(notification, true);
};
