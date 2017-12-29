//Event triggered by finishing quiz
function send_report(score, total, dif)
{
	var data = "score=" + score + "&total=" + total + "&dif=" + dif;
	makeRequest('POST', '/report/', do_nothing, 201, data);
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
function handleReports()
{
	
}