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
	var rep = JSON.parse(data);
	var reports = JSON.parse(rep);	//Double stringed data
	for(i in reports)
	{
		//Display each report individually
		display_report(reports[i]['date'], reports[i]['dif'], reports[i]['total'], reports[i]['score'])
	}
}

//Display an individual report
function display_report(date, dif, total, correct)
{
	console.log(date + " " + dif + " " + total + " " + correct);
}

//Display overall statistics for all reports
function get_overall()
{

}