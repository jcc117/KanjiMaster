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

//Show an update message for a successful change of information
function display_success()
{

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

	//Add event listeners for change buttons
	document.getElementById("change_e").addEventListener("click", change_email, true);
	document.getElementById("change_p").addEventListener("click", change_password, true);
}

window.addEventListener("load", s_setup, true);