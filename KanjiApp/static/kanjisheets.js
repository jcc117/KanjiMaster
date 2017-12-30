//Get all kanji
function get_kanji()
{
	makeRequest('GET', "/kanji/", make_table, 200);
}

//Make the table of kanji
function make_table(data)
{

}