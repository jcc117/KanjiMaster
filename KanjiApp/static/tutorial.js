function t_setup()
{
	$('#tspan').click(start);
}


function start()
{
	alert("hello");
	//Able to use request functions from function.js
}

window.addEventListener("load", t_setup, true);