//Report functions

//for overall stats
var total_q = 0;
var scores = 0;
var num_reports = 0;

function r_setup()
{
	//Get the reports for the page
	get_report();

	$('#refresh').click(function(){ refresh(); });
}
//Event triggered by finishing quiz
function send_report(score, total, dif)
{
	console.log(score + " " + total + " " + dif);
	var data = "score=" + score + "&total=" + total + "&dif=" + dif;
	makeRequest('POST', '/report/', do_nothing, 201, data, 'application/x-www-form-urlencoded');
}

//Filler for above
function do_nothing()
{

}

//Ask for all reports for a user
function get_report()
{
	makeRequest('GET', '/report/', handleReports, 200);
}

//Handle all of the reports from the request
function handleReports(data)
{
	var reports = JSON.parse(JSON.parse(data));	//Data is double stringed
	for(i in reports)
	{
		//Display each report individually
		display_report(reports[i]['date'], reports[i]['dif'], reports[i]['total'], reports[i]['score']);
		total_q += reports[i]['total'];
		scores += reports[i]['score'];
		num_reports++;
	}

	get_overall();
}

//Display an individual report
function display_report(date, dif, total, correct)
{
	//Temporary
	console.log(date + " " + dif + " " + total + " " + correct);

	var ind = document.getElementById("ind");

	//Create and format the new element
	var elem = document.createElement("div");
	elem.classList.add("report");

	elem.appendChild(document.createTextNode("Date:\t" + date));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Difficulty:\t" + dif));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Total Questions:\t" + total));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Score:\t" + correct));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Percentage:\t" + ((correct/total)* 100) + "%"));
	elem.appendChild(document.createElement("br"));

	//Append the new report to the list
	ind.appendChild(elem);
}

//Display overall statistics for all reports
function get_overall()
{
	var overall = document.getElementById("overall");

	//Create the element and format it
	var elem = document.createElement("div");
	elem.classList.add("report");

	elem.appendChild(document.createTextNode("Total Questions Answered:\t" + total_q));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Total Questions Answered Correctly:\t" + scores));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Overall Percentage:\t" + ((scores/total_q)* 100) + "%"));
	elem.appendChild(document.createElement("br"));
	elem.appendChild(document.createTextNode("Number of Quizzes Taken:\t" + num_reports));
	elem.appendChild(document.createElement("br"));

	//Add the div to the page
	overall.appendChild(elem);
}

//Refresh the reports you have on the page
function refresh()
{
	//Clear out the page
	document.getElementById('ind').innerHTML = '';
	document.getElementById('overall').innerHTML = '';

	total_q = 0;
	scores = 0;
	num_reports = 0;

	//Repopulate it
	get_report();
}

//Initialize page setup on load time
window.addEventListener("load", r_setup, true);