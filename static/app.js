
$(document).ready(function(){
$("#post").click(function(){
    content = $("#content_post").html();


  $.post("/create_post",
  {
    content: content
  },
  function(data, status){
    //alert("Data: " + data + "Status: " + status);
    if(data['status'] ==  "fail"){
        alert("Please Try again.")
    }else{
    $("#post_body").prepend(data)
    }
    $("#content_post").html("");

  });
});

});

function sayHello() {
   alert("Hello World")
}

// Accordion
function myFunction(id) {
  var x = document.getElementById(id);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    x.previousElementSibling.className += " w3-theme-d1";
  } else {
    x.className = x.className.replace("w3-show", "");
    x.previousElementSibling.className =
    x.previousElementSibling.className.replace(" w3-theme-d1", "");
  }
}

// Used to toggle the menu on smaller screens when clicking on the menu button
function openNav() {
  var x = document.getElementById("navDemo");
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
}

