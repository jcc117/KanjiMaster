var timeoutID;
var timeout = 1000;

var kanji = [];
var romaji = [];
var score = 0;
var total = 30;
var turn = 1;

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
	var game = document.getElementById("game");
	game.style.display = "none";

	//timeoutID = window.setTimeout(poller, timeout);
}

//Switch visibility of which screen you are looking at
function switch_to_q()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");

	qu.style.display = "none";
	q.style.display = "block";
	r.style.display = "none";
}
function switch_to_r()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");

	qu.style.display = "none";
	r.style.display = "block";
	q.style.display = "none";
}

//Make a function to dynamically handle all requests
function makeRequest(method, to, action,data)
{
	//alert("making request");
	var httpRequest = new XMLHttpRequest();
	if(!httpRequest)
	{
		alert("Requests are not supported");
		return false;
	}

	httpRequest.onreadystatechange = makeHandler(httpRequest, action);
	//console.log(httpRequest.onreadystatechange);
	httpRequest.open(method, to);
	if(data)
	{
		httpRequest.setRequestHeader('Content-Type', 'application/json');
		httpRequest.send(data);
	}
	else
	{
		httpRequest.send();
	}
}

//Return a handler for a general request
function makeHandler(httpRequest, action)
{
	function handler()
	{
		if(httpRequest.readyState === XMLHttpRequest.DONE)
		{
			//alert("done");
			if(httpRequest.status === 200)
			{
				if(httpRequest.responseText)
					console.log("recieved response text: " + JSON.parse(httpRequest.responseText));
				//else
					//alert("I got nothin");
				action(httpRequest.responseText);
			}
			else
			{
				alert("There was a problem with the request");
				console.log("Error: " + JSON.parse(httpRequest.responseText));
			}
		}
	}
	//alert("function returned");
	return handler;
}

function parseData(data)
{
	//document.write("returned: " + JSON.parse(data));
	//alert(data);
	var pData = JSON.parse(data);

	for(i in pData)
	{
		var result = pData[i].split(":");
		kanji[i] = result[0];
		romaji[i] = result[1];
		//console.log(result[1]);
		//console.log("kanji:" + kanji[i] + ", romaji:" + romaji[i]);
	}

	var q = document.getElementById("quiz");
	q.style.display = "none";
	var r = document.getElementById("reports");
	r.style.display = "none";
	var g = document.getElementById("game");
	g.style.display = "block";

	quiz_setup();
	
}

//Take a quiz after all information is gathered
function quiz_setup()
{
	if(turn <= total)
	{
		//Set up the quit button
		document.getElementById("quit").addEventListener("click", quit, true);

		//Retrieve all choice buttons
		var c1 = document.getElementById("c1");
		var c2 = document.getElementById("c2");
		var c3 = document.getElementById("c3");
		var c4 = document.getElementById("c4");

		//Randomly select a kanji to test
		var cor = Math.floor((Math.random() * romaji.length));
		var cor_str = romaji[cor];
		var cor_kan = kanji[cor];

		//Randomly select other 3 other
		var selected_nums = [];
		selected_nums[0] = cor;
		var num = 1;
		while(num < 4)
		{
			var next = Math.floor((Math.random() * romaji.length));
			var found = false;

			//Check that number wasn't already selected
			for(i in selected_nums)
			{
				if(selected_nums[i] === next)
				{
					found = true;
					break;
				}
			}

			if(!found)
			{
				selected_nums[num++] = next;
			}
		}

		//For now, just set the answers up in the given order
		c1.value = romaji[selected_nums[0]];
		c2.value = romaji[selected_nums[1]];
		c3.value = romaji[selected_nums[2]];
		c4.value = romaji[selected_nums[3]];

		c1.addEventListener("click", correct, true);
		c2.addEventListener("click", wrong, true);
		c3.addEventListener("click", wrong, true);
		c4.addEventListener("click", wrong, true);
	}
	else
	{
		show_results();
	}
}

function show_results()
{
	//Temporary
	console.log("score: " + score);
	console.log("total: " + total);
}

function correct()
{
	score++;
	turn++;
	quiz_setup();
}

function wrong()
{
	turn++;
	quiz_setup();
}

//Quit a quiz and return to a menu
function quit()
{
	//reset all variables
	score = 0;
	turn = 1;
	kanji = [];
	romaji = [];

	//set visibility of pages
	switch_to_q();
}

function quiz1()
{
	makeRequest('POST', "/kanji/", parseData, 1);
	console.log('plz');
}

function quiz2()
{
	makeRequest('POST', "/kanji/", parseData, 2);
}

function quiz3()
{
	makeRequest('POST', "/kanji/", parseData, 3);
}

function quiz4()
{
	makeRequest('POST', "/kanji/", parseData, 4);
}

function quiz5()
{
	makeRequest('POST', "/kanji/", parseData, 5);
}

function quiz6()
{
	makeRequest('POST', "/kanji/", parseData, 6);
}

//Initialize page setup on load time
window.addEventListener("load", setup, true);

/*
$.ready(function($){

	$('.sticker').mouseenter(function() {
		if ($(this).is(':animated')) {return;}
		$(this).animate({ bottom: "+=60" }, {duration: 120, easing: "easeOutQuart"})
		.animate({ bottom: "-=60" }, {duration: 150, easing: "easeInSine"});
	});
});*/

