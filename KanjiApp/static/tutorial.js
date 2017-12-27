function t_setup()
{
	$('#tspan').click(start);
}

function start()
{
	alert("hello");
}

window.addEventListener("load", t_setup, true);