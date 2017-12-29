//Event triggered by finishing quiz
function send_report(score, total, dif)
{
	makeRequest('POST', '/report/', do_nothing, 201, [score, total, dif]);
}

//Filler for above
function do_nothing()
{

}