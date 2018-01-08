//Quiz related functions

var kanji = [];
var romaji = [];
var score = 0;
var total = 30;
var turn = 1;
var cor;
var dif = 0;

//Parse data related from quiz request
function parseData(data)
{
	//document.write("returned: " + JSON.parse(data));
	//alert(data);
	var rData = JSON.parse(JSON.parse(data));
	var pData = rData.filter(filter_dif);

	//console.log("pData: " + pData);

	for(i in pData)
	{
		//var result = pData[i].split(":");
		kanji[i] = pData[i]['kanji'];
		romaji[i] = pData[i]['romaji'];
		//console.log(result[1]);
		//console.log("kanji:" + kanji[i] + ", romaji:" + romaji[i]);
	}

	var q = document.getElementById("quiz");
	q.style.display = "none";
	var r = document.getElementById("reports");
	r.style.display = "none";
	var g = document.getElementById("game");
	g.style.display = "block";

	//Start audio
	var audio = document.getElementById("gameAudio");
	audio.load();
	audio.play();

	$("#s_sticker").show();
	$("#s_sticker2").hide();

	quiz_setup();
	
}

function filter_dif(item)
{
	return item['dif'] === dif;
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
		cor = Math.floor((Math.random() * romaji.length));
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

		//Randomize the order of the array
		selected_nums = shuffle(selected_nums);

		clear_listeners();

		//Assign all values and event listeners
		//At least one of these if statements should trigger adding the event listeners
		//console.log("cor is " + cor);
		//console.log("numbers: " + selected_nums);
		c1.value = romaji[selected_nums[0]];
		if(selected_nums[0] === cor)
		{
			//console.log("a is right");
			c1.addEventListener("click", correct);
			c2.addEventListener("click", wrong);
			c3.addEventListener("click", wrong);
			c4.addEventListener("click", wrong);
		}
		c2.value = romaji[selected_nums[1]];
		if(selected_nums[1] === cor)
		{
			//console.log("b is right");
			c1.addEventListener("click", wrong);
			c2.addEventListener("click", correct);
			c3.addEventListener("click", wrong);
			c4.addEventListener("click", wrong);
		}
		c3.value = romaji[selected_nums[2]];
		if(selected_nums[2] === cor)
		{
			//console.log("c is right");
			c1.addEventListener("click", wrong);
			c2.addEventListener("click", wrong);
			c3.addEventListener("click", correct);
			c4.addEventListener("click", wrong);
		}
		c4.value = romaji[selected_nums[3]];
		if(selected_nums[3] === cor)
		{
			//console.log("d is right");
			c1.addEventListener("click", wrong);
			c2.addEventListener("click", wrong);
			c3.addEventListener("click", wrong);
			c4.addEventListener("click", correct);
		}

		//Display the question
		document.getElementById("question").textContent=cor_kan;
		
		/*
		c1.addEventListener("click", correct, true);
		c2.addEventListener("click", wrong, true);
		c3.addEventListener("click", wrong, true);
		c4.addEventListener("click", wrong, true);
		*/
	}
	else
	{
		show_results();
	}
}

//Remove all event listeners from the buttons
function clear_listeners()
{
	var c1 = document.getElementById("c1");
	var c2 = document.getElementById("c2");
	var c3 = document.getElementById("c3");
	var c4 = document.getElementById("c4");

	c1.removeEventListener("click", wrong);
	c1.removeEventListener("click", correct);
	c2.removeEventListener("click", wrong);
	c2.removeEventListener("click", correct);
	c3.removeEventListener("click", wrong);
	c3.removeEventListener("click", correct);
	c4.removeEventListener("click", wrong);
	c4.removeEventListener("click", correct);
}

//Shuffle the array of answers to assign to buttons
function shuffle(array)
{
	var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) 
  {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

function show_results()
{
	//Temporary
	console.log("score: " + score);
	console.log("total: " + total);
	send_report(score, total, dif);
	switch_to_r();
	refresh();
}

function correct()
{
	score++;
	turn++;

	//Play sound effect
	var ping = document.getElementById("ping");
	ping.load();
	var promise = ping.play();

	if(promise !== undefined)
	{
		promise.then(_ => {
			console.log("yay")
		})
		.catch(error => {
			console.log("error in sound effect");
		});
	}

	$('#feedback').html('Correct!').removeClass('invalid').addClass('valid');

	$("#s_sticker").hide();
	$("#s_sticker2").show();

		if ($('#s_sticker2').is(':animated')) {return;}
		$('#s_sticker2').animate({ bottom: "+=60" }, {duration: 120, easing: "easeOutQuart"})
		.animate({ bottom: "-=60" }, {duration: 150, easing: "easeInSine"});

	quiz_setup();
}

function wrong()
{
	$('#feedback').html('Wrong: the answer was ' + romaji[cor]).removeClass('valid').addClass('invalid');

	$("#s_sticker2").hide();
	$("#s_sticker").show();

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

	$('#feedback').html('');

	var audio = document.getElementById("gameAudio");
	audio.pause();

	//set visibility of pages
	switch_to_q();
}

function quiz1()
{
	dif = 1;
	makeRequest('GET', "/kanji/", parseData, 200);
	//console.log('plz');
}

function quiz2()
{
	alert("That is not yet supported");
	/*dif = 2;
	makeRequest('GET', "/kanji/", parseData, 200);*/
}

function quiz3()
{
	alert("That is not yet supported");
	/*dif = 3;
	makeRequest('GET', "/kanji/", parseData, 200);*/
}

function quiz4()
{
	alert("That is not yet supported");
	/*dif = 4;
	makeRequest('GET', "/kanji/", parseData, 200);*/
}

function quiz5()
{
	alert("That is not yet supported");
	/*dif = 5;
	makeRequest('GET', "/kanji/", parseData, 200);*/
}

function quiz6()
{
	alert("That is not yet supported");
	/*dif = 6;
	makeRequest('GET', "/kanji/", parseData, 200);*/
}