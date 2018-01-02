//Request information about the user
function s_setup()
{
	makeRequest("GET", "/user/", setup_info, 200);
}

//Set up all of the info about the user
function setup_info(data)
{
	//Parse data
	var pData = JSON.parse(JSON.parse(data));

	//Display the data
	document.getElementById("userID").innerHTML = pData[0]['userID'];
	document.getElementById("email").innerHTML = pData[0]['email'];
	document.getElementById("fname").innerHTML = pData[0]['fname'];
	document.getElementById("lname").innerHTML = pData[0]['lname'];
}

window.addEventListener("load", s_setup, true);