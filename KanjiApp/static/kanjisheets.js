//Table of all kanji
var all_kanji;

//Setup the kanji table updon loading
function k_setup()
{
	get_kanji();
}


//Get all kanji
function get_kanji()
{
	makeRequest('GET', "/kanji/", make_table, 200);
}

//Make the table of kanji
function make_table(data)
{
	all_kanji = data;	//Hold this data for use for the quizzes
	
	var pData = JSON.parse(JSON.parse(data)); //Double parsed data

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
	var elem = document.createElement("tr");
	elem.classList.add("row");

	//Create each column, each containing a data item
	var k = document.createElement("td");
	var r = document.createElement("td");
	var d = document.createElement("td");

	k.classList.add("column");
	r.classList.add("column");
	d.classList.add("column");

	k.appendChild(document.createTextNode(kanji));
	r.appendChild(document.createTextNode(romaji));
	d.appendChild(document.createTextNode(dif));

	elem.appendChild(d);
	elem.appendChild(k);
	elem.appendChild(r);

	table.appendChild(elem);
}

//Initialize page setup on load time
window.addEventListener("load", k_setup, true);