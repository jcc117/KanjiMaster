//Table of all kanji
var all_kanji;
var s_dif = 0;
var p_data;

//Setup the kanji table updon loading
function k_setup()
{
	document.getElementById("search").addEventListener("click", search, true);
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
	p_data = pData;

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
	//Get the lesson
	var lesson;
	if(dif === 1)
	{
		lesson = "Lesson 9";
	}
	else if(dif === 2)
	{
		lesson = "Lesson 10";
	}
	else if(dif === 3)
	{
		lesson = "Lesson 11";
	}
	else if(dif === 4)
	{
		lesson = "Lesson 12";
	}
	else if(dif === 5)
	{
		lesson = "Lesson 13";
	}
	else if(dif === 6)
	{
		lesson = "Lesson 14";
	}
	else if(dif === 7)
	{
		lesson = "Lesson 15";
	}
	else if(dif === 0)
	{
		lesson = "Hiragana";
	}
	else if(dif === -1)
	{
		lesson = "Katakana";
	}
	d.appendChild(document.createTextNode(lesson));

	elem.appendChild(d);
	elem.appendChild(k);
	elem.appendChild(r);

	table.appendChild(elem);
}

//Search for kanji of a specific difficulty
function search()
{
	//Get the value you are searching for
	var selection = document.getElementById("k_option").value;
	//console.log(selection);
	//If all kanji are selected, just run make_table again
	if(selection === "All")
	{
		clear_table();
		make_table(all_kanji);
	}
	//Select a specific lesson
	else
	{
		//Find the corresponding number for the lesson selection
		set_dif(selection);
		//var pData = JSON.parse(all_kanji);
		//console.log("pData:" + pData);
		var filtered = p_data.filter(filter_by_dif);
		console.log(filtered);
		clear_table();
		var table = document.getElementById("table");
		//Add all results to the table
		for(i in filtered)
		{
			add_row(table, filtered[i]['kanji'], filtered[i]['romaji'], filtered[i]['dif']);
		}
	}
}
function filter_by_dif(item)
{
	return item['dif'] === s_dif;
}
//Clear the table
function clear_table()
{
	var table = document.getElementById("table");
	while(table.firstChild)
	{
		table.removeChild(table.firstChild);
	}
	//Reinsert headers
	var h1 = document.createElement("th");
	var h2 = document.createElement("th");
	var h3 = document.createElement("th");
	h1.appendChild(document.createTextNode("Lesson"));
	h2.appendChild(document.createTextNode("Kanji"));
	h3.appendChild(document.createTextNode("Reading"));

	table.appendChild(h1);
	table.appendChild(h2);
	table.appendChild(h3);
}
//Set the s_dif(selected difficulty) to the corresponding number based on lesson selection
function set_dif(selection)
{
	if(selection === "Hiragana")
		s_dif = 0;
	else if(selection === "Katakana")
		s_dif = -1;
	else if(selection === "Lesson9")
		s_dif = 1;
	else if(selection === "Lesson10")
		s_dif = 2;
	else if(selection === "Lesson11")
		s_dif = 3;
	else if(selection === "Lesson12")
		s_dif = 4;
	else if(selection === "Lesson13")
		s_dif = 5;
	else if(selection === "Lesson14")
		s_dif = 6;
	else if(selection === "Lesson15")
		s_dif = 7;

	//console.log(s_dif);
}

//Initialize page setup on load time
window.addEventListener("load", k_setup, true);