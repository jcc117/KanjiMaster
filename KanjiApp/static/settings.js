//Request information about the user
function s_setup()
{
	makeRequest("GET", "/user/", setup_info, 200);
}

//Request to change email
function change_email()
{
	var data = "email=" + document.getElementById("new_email").value;

	makeRequest("POST", "/change_email/", display_success, 200, data, 'application/x-www-form-urlencoded');
}

//Request to change password
function change_password()
{
	var data = "password=" + document.getElementById("pass2").value;

	makeRequest("POST", "/change_pass/", display_success, 200, data, 'application/x-www-form-urlencoded');
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