
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