var timeoutID;
var timeout = 1000;

//Set up the page
function setup()
{
	document.getElementById("g1").addEventListener("click", quiz1, true);
	document.getElementById("g2").addEventListener("click", quiz2, true);
	document.getElementById("g3").addEventListener("click", quiz3, true);
	document.getElementById("g4").addEventListener("click", quiz4, true);
	document.getElementById("g5").addEventListener("click", quiz5, true);
	document.getElementById("g6").addEventListener("click", quiz6, true);
	document.getElementById("qspan").addEventListener("click", switch_to_q, true);
	document.getElementById("rspan").addEventListener("click", switch_to_r, true);

	var rep = document.getElementById("reports");
	rep.style.display = "none";

	//timeoutID = window.setTimeout(poller, timeout);
}

//Switch visibility of which screen you are looking at
function switch_to_q()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");

	q.style.display = "block";
	r.style.display = "none";
}
function switch_to_r()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");

	r.style.display = "block";
	q.style.display = "none";
}

//Make a function to dynamically handle all requests
function makeRequest(method, to, data)
{
	var httpRequest = new XMLHttpRequest();
	if(!httpRequest)
	{
		alert("Requests are not supported");
		return false;
	}

	httpRequest.onreadystatechange = function(){ handleRequest(httpRequest)};
	if(data)
	{
		httpRequest.setRequestHeader('Content-Type', 'application/json');
		httpRequest.open(method, to, data);
	}
	else
	{
		httpRequest.open(method, to)
	}
	httpRequest.send();
}

//These requests will only have to handle getting kanji data
//They only have to get the data to populate the quiz tables
function handleRequest(httpRequest)
{
	if(httpRequest.readyState === XMLHttpRequest.DONE)
	{
		if(httpRequest.status === 200)
		{

		}
		else
		{
			alert("A problem occured. Please reload the page.");
		}
	}
}

function quiz1()
{
	makeRequest('POST', 1);
}

function quiz2()
{
	makeRequest('POST', 2);
}

function quiz3()
{
	makeRequest('POST', 3);
}

function quiz4()
{
	makeRequest('POST', 4);
}

function quiz5()
{
	makeRequest('POST', 5);
}

function quiz6()
{
	makeRequest('POST', 5);
}

//Initialize page setup on load time
window.addEventListener("load", setup, true);

$.ready(function($){

	$('.sticker').mouseenter(function() {
		if ($(this).is(':animated')) {return;}
		$(this).animate({ bottom: "+=60" }, {duration: 120, easing: "easeOutQuart"})
		.animate({ bottom: "-=60" }, {duration: 150, easing: "easeInSine"});
	});
});

