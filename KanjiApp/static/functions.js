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
	document.getElementById("g7").addEventListener("click", quiz7, true);
	document.getElementById("hi").addEventListener("click", quiz0, true);
	document.getElementById("ka").addEventListener("click", quizn1, true);
	document.getElementById("qspan").addEventListener("click", switch_to_q, true);
	document.getElementById("rspan").addEventListener("click", switch_to_r, true);
	document.getElementById("kspan").addEventListener("click", switch_to_k, true);
	document.getElementById("sspan").addEventListener("click", switch_to_s, true);
	document.getElementById("lspan").addEventListener("click", switch_to_l, true);
	document.getElementById("aspan").addEventListener("click", switch_to_a, true);
	document.getElementById("mspan").addEventListener("click", switch_to_m, true);

	var rep = document.getElementById("reports");
	rep.style.display = "none";
	var game = document.getElementById("game");
	game.style.display = "none";
	var sheets = document.getElementById("sheets");
	sheets.style.display = "none";
	var set = document.getElementById("settings");
	set.style.display = "none";
	var links = document.getElementById("links");
	links.style.display = "none";
	var quiz = document.getElementById("quiz");
	quiz.style.display = "none";
	var m = document.getElementById("mnemonics");
	m.style.display = "none";

}

//Switch visibility of which screen you are looking at
function switch_to_q()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "none";
	a.style.display = "none";
	l.style.display = "none";
	qu.style.display = "none";
	q.style.display = "block";
	r.style.display = "none";
	k.style.display = "none";
	s.style.display = "none";

	quiz_reset();
}
function switch_to_r()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "none";
	a.style.display = "none";
	l.style.display = "none";
	qu.style.display = "none";
	r.style.display = "block";
	q.style.display = "none";
	k.style.display = "none";
	s.style.display = "none";

	quiz_reset();
}
//Swtich to the kanjisheets
function switch_to_k()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "none";
	a.style.display = "none";
	l.style.display = "none";
	qu.style.display = "none";
	r.style.display = "none";
	q.style.display = "none";
	k.style.display = "block";
	s.style.display = "none";

	quiz_reset();
}
//Switch to user settings
function switch_to_s()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "none";
	a.style.display = "none";
	l.style.display = "none";
	qu.style.display = "none";
	r.style.display = "none";
	q.style.display = "none";
	k.style.display = "none";
	s.style.display = "block";

	quiz_reset();
}
//Switch to external links
function switch_to_l()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "none";
	a.style.display = "none";
	l.style.display = "block";
	qu.style.display = "none";
	r.style.display = "none";
	q.style.display = "none";
	k.style.display = "none";
	s.style.display = "none";

	quiz_reset();
}

//Switch to about us
function switch_to_a()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "none";
	a.style.display = "block";
	l.style.display = "none";
	qu.style.display = "none";
	r.style.display = "none";
	q.style.display = "none";
	k.style.display = "none";
	s.style.display = "none";

	quiz_reset();
}

//Switch to about us
function switch_to_m()
{
	var q = document.getElementById("quiz");
	var r = document.getElementById("reports");
	var qu = document.getElementById("game");
	var k = document.getElementById("sheets");
	var s = document.getElementById("settings");
	var l = document.getElementById("links");
	var a = document.getElementById("about");
	var m = document.getElementById("mnemonics");

	m.style.display = "block";
	a.style.display = "none";
	l.style.display = "none";
	qu.style.display = "none";
	r.style.display = "none";
	q.style.display = "none";
	k.style.display = "none";
	s.style.display = "none";

	quiz_reset();
}

function quiz_reset()
{
	//var audio = document.getElementById("gameAudio");
	//audio.pause();

	score = 0;
	turn = 1;
}

//Make a function to dynamically handle all requests
function makeRequest(method, to, action, retcode, data, encoding)
{
	//alert("making request");
	var httpRequest = new XMLHttpRequest();
	if(!httpRequest)
	{
		alert("Requests are not supported");
		return false;
	}

	httpRequest.onreadystatechange = makeHandler(httpRequest, retcode, action);
	//console.log(httpRequest.onreadystatechange);
	httpRequest.open(method, to);
	if(data)
	{
		httpRequest.setRequestHeader('Content-Type', encoding);
		httpRequest.send(data);
	}
	else
	{
		httpRequest.send();
	}
}

//Return a handler for a general request
function makeHandler(httpRequest, retcode, action)
{
	function handler()
	{
		if(httpRequest.readyState === XMLHttpRequest.DONE)
		{
			//alert("done");
			if(httpRequest.status === retcode)
			{
				if(httpRequest.responseText)
					console.log("recieved response text: " + JSON.parse(httpRequest.responseText));
				else
					alert("I got nothin");
				action(httpRequest.responseText);
			}
			else
			{
				alert(httpRequest.status + ":There was a problem with the request");
				console.log("Error: " + JSON.parse(httpRequest.responseText));
			}
		}
	}
	//alert("function returned");
	return handler;
}


jQuery(function($){

	$('.sticker').mouseenter(function() {
		if ($(this).is(':animated')) {return;}
		$(this).animate({ bottom: "+=60" }, {duration: 120, easing: "easeOutQuart"})
		.animate({ bottom: "-=60" }, {duration: 150, easing: "easeInSine"});
	});
	/*
	var audio = $("#but_hov")[0];
	$('.choice').mouseenter(function(){audio.load(); audio.play();});*/
});

//Loader image
$(window).on('load', function(){
	$('#loader').fadeOut(500);
});

//Ajax loader image
$(document).ajaxStart(function(){
	$('#loader').show();
}).ajaxStop(function(){
	$('#loader').fadeOut(500);
})

//Initialize page setup on load time
window.addEventListener("load", setup, true);