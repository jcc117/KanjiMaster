//Setup the tutorial function
function t_setup()
{
	$('#tspan').click(start);
}

//Run the tutorial
function start()
{
	switch_to_q();
	explain_q();
	switch_to_r();
	explain_r();
	switch_to_k();
	explain_k();
	switch_to_s();
	explain_s();
	alert("Not yet supported");
	//Able to use request functions from function.js
}

//Explain how quizzes work
function explain_q()
{

}

//Explain reports
function explain_r()
{

}

//Explain the kanji sheets
function explain_k()
{

}

//Explain user settings
function explain_s()
{

}

window.addEventListener("load", t_setup, true);