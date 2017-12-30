//Get all kanji
function get_kanji()
{
	makeRequest('GET', "/kanji/", make_table, 200);
}

//Make the table of kanji
function make_table(data)
{
	var pData = JSON.parse(JSON.parse(data));

	//Add rows the table of kanji

	var table = document.getElementById("table");
	for(i in pData)
	{
		add_row(table, pData[i]['kanji'], pData[i]['romaji'], pData[i]['dif']);
	}
}

//Add a row of kanji to the table
function add_row(table, kanji, romaji, dif)
{
	//Create outer container
	var elem = document.createElement("div");
	elem.classList.add("row");

	//Create each column, each containing a data item
}