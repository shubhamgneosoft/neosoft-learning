
$(document).ready(function(){
$("#post").click(function(){

  $.post("/create_post",
  {
    content: $("#content_post").html(),
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

  $(".like_post").click(function(e){
      post_id = e.target.id
      $.post("/like_post",
      {
        post_id: post_id,
      },
      function(data, status){
        //alert("Data: " + data + "Status: " + status);
        if(data['status'] ==  "success"){
            $("#"+post_id+" .w3-badge").html(data['count'])
            console.log(data['count'])
        }else{
            alert("Please Try Again.")
        }

  })

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

