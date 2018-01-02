
var myInput = document.getElementById("pass");
var myInput2 = document.getElementById("pass2");
var msg = document.getElementById("msg");
var letter = document.getElementById("lc");
var capital = document.getElementById("cap");
var number = document.getElementById("number");
var length = document.getElementById("length");

// When the user clicks on the password field, show the message box
myInput.onfocus = function() {
  document.getElementById("message").style.display = "block";
}

myInput2.onfocus = function() {
  document.getElementById("confirm").style.display = "block";
}

// When the user clicks outside of the password field, hide the message box
myInput.onblur = function() {
  document.getElementById("message").style.display = "none";
}

myInput2.onblur = function() {
  document.getElementById("confirm").style.display = "none";
}

// When the user starts to type something inside the password field
myInput.onkeyup = function() {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) { 
    letter.classList.remove("invalid");
    letter.classList.add("valid");
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
}

  // Validate capital letters
  var upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) { 
    capital.classList.remove("invalid");
    capital.classList.add("valid");
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
  }

  // Validate numbers
  var numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) { 
    number.classList.remove("invalid");
    number.classList.add("valid");
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
  }

  // Validate length
  if(myInput.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
}

//Password confirmation
myInput2.onkeyup = function() {
  if(myInput2.value === myInput.value)
  {
    msg.classList.remove("invalid");
    msg.classList.add("valid");
  }
  else
  {
    msg.classList.remove("valid");
    msg.classList.add("valid");
  }
}

//Loader image
$(window).on('load', function(){
  $('#loader').fadeOut(500);
});

//Ajax loader image
$(document).ajaxStart(function(){
  $('#loader').show();
}).ajaxStop(function(){
  $('#loader').fadeOut(500);
})

function signup()
{
  var userID = document.getElementById("name").value;
  var password = document.getElementById("pass").value;
  var fname = document.getElementById("fname").value;
  var lname = document.getElementById("lname").value;
  var email = document.getElementById("email").value;
  var pass2 = document.getElementById("pass2").value;

  var data = "userID=" + userID + "&pass=" + password + "&fname=" + fname + "&lname=" + lname + "&email=" + email + "&pass2="+pass2;

  makeRequest("POST", "/user/", go_to_root, 201, data, 'application/x-www-form-urlencoded');
}

function go_to_root()
{
  makeRequest("GET", "/", do_nothing, 200);
}

function do_nothing()
{

}

function setup()
{
  document.getElementById("signup").addEventListener("click", signup, true);
}

/*Taken from functions.js*/

//Make a function to dynamically handle all requests
function makeRequest(method, to, action, retcode, data, encoding)
{
  //alert("making request");
  var httpRequest = new XMLHttpRequest();
  if(!httpRequest)
  {
    alert("Requests are not supported");
    return false;
  }

  httpRequest.onreadystatechange = makeHandler(httpRequest, retcode, action);
  //console.log(httpRequest.onreadystatechange);
  httpRequest.open(method, to);
  if(data)
  {
    httpRequest.setRequestHeader('Content-Type', encoding);
    httpRequest.send(data);
  }
  else
  {
    httpRequest.send();
  }
}

//Return a handler for a general request
function makeHandler(httpRequest, retcode, action)
{
  function handler()
  {
    if(httpRequest.readyState === XMLHttpRequest.DONE)
    {
      //alert("done");
      if(httpRequest.status === retcode)
      {
        if(httpRequest.responseText)
          console.log("recieved response text: " + JSON.parse(httpRequest.responseText));
        else
          alert("I got nothin");
        action(httpRequest.responseText);
      }
      else
      {
        alert(httpRequest.status + ":There was a problem with the request");
        console.log("Error: " + JSON.parse(httpRequest.responseText));
      }
    }
  }
  //alert("function returned");
  return handler;
}

//Initialize page setup on load time
window.addEventListener("load", setup, true);