var i = 0;
var speed = 50;

//Setup the tutorial function
function t_setup()
{
	$('#tspan').click(start);
	document.getElementById('d1').style.display = "none";
}

//Run the tutorial
function start()
{
	document.getElementById('d1').style.display = "block";
	clear();
	document.getElementById("n1").addEventListener("click", explain_q2, true);
	switch_to_q();
	explain_q1();
	//switch_to_r();
	/*explain_r();
	switch_to_k();
	explain_k();
	switch_to_s();
	explain_s();*/
	//Clear the dialouge box
	clear();
	alert("Not yet supported");
	//Able to use request functions from function.js
}

//Explain how quizzes work
function explain_q1()
{
	var text = "Welcome to KanjiMaster.com! We'll guide you through some of the basics of this site."
	typeWriter(text, i);
}
function explain_q2()
{
	clear();
	var text =  "This is the quiz tab, where you can take quizzes. Each grade level tests you on a different set of kanji. By clicking on the correct button, you will be tested on 30 random kanji compounds."
	typeWriter(text, i);
	document.getElementById("n1").removeEventListener("click", explain_q2);
	document.getElementById("n1").addEventListener("click", explain_r, true);
}

//Explain reports
function explain_r()
{
	clear();
	switch_to_r();
}

//Explain the kanji sheets
function explain_k()
{

}

//Explain user settings
function explain_s()
{

}

//Have typewriter effect for text
function typeWriter(text, i)
{
	console.log(text.charAt(i) + i);
	if(i < text.length)
	{
		document.getElementById("p1").innerHTML += text.charAt(i);
		i++;
		setTimeout(function(){typeWriter(text, i)}, speed);
	}
}

//Clear the dialouge box
function clear()
{
	document.getElementById("p1").innerHTML = '';
	i = 0;
}

window.addEventListener("load", t_setup, true);