var latest_date;

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

//Request change to reason for learning kanji
function change_reason()
{
	var data = "reason=" + document.getElementById("new_reason").value;

	makeRequest("POST", "/change_reason/", display_success_r, 200, data, 'application/x-www-form-urlencoded');
}

//Show an update message for a successful change of information
function display_success()
{
	var message = document.getElementById("response");
	message.innerHTML = "Success!";
	message.classList.add('valid');
	makeRequest("GET", "/user/", setup_info, 200);
}

function display_success_r()
{
	var message = document.getElementById("reason_response");
	message.innerHTML = "Success!";
	message.classList.add('valid');
	makeRequest("GET", "/user/", setup_info, 200);
}

function change_css()
{
	var file = document.getElementById("gemstone").value;
	var csslink = document.getElementById("css");
	csslink.setAttribute("href", file);
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
	//Set this up for the main header
	document.getElementById("reason").innerHTML = "Remember your reason for studying Kanji! - " + pData[0]['reason'];

	latest_date = new Date(pData[0]['date']);

	//Add event listeners for change buttons
	document.getElementById("change_e").addEventListener("click", change_email, true);
	document.getElementById("change_r").addEventListener("click", change_reason, true);
	document.getElementById("change_c").addEventListener("click", change_css, true);

	//Set up info for weekly goals
	var goal = pData[0]['weekly_goal'];
	var goal_ts = new Date(pData[0]['goal_ts']);

	//Check if a week has passed to set up a weekly goal
	if((Date.now() - goal_ts.valueOf()) >= (60000 * 60 * 24 * 7))
	{
		var new_goal = prompt("It's time to set up a new goal for the week! Please keep your goal reasonable. If you're learning more kanji, try to keep that number low enough to be achievable (10-15).");
		var data = "goal=" + new_goal;
		makeRequest("POST", "/change_weekly_goal/", do_nothing, 200, data, 'application/x-www-form-urlencoded');
		document.getElementById("weekly_goal").innerHTML = "Your weekly goal - " + new_goal;
	}
	else
	{
		document.getElementById("weekly_goal").innerHTML = "Your weekly goal - " + goal; 
	}
}

window.addEventListener("load", s_setup, true);