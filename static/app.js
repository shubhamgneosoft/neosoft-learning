
$(document).ready(function(){

var socket_cp = io.connect('http://127.0.0.1:5000/create_post');

  $("#post").click(function(e){
    socket_cp.send($("#content_post").html());
    $("#content_post").html("");
  });
  socket_cp.on('message', function(data) {
     $("#post_body").prepend(data)
  });

var socket_lp = io.connect('http://127.0.0.1:5000/like_post');

  $(".like_post").click(function(e){
    post_id = e.target.id
    console.log(post_id)
    socket_lp.send(post_id);
  });
  socket_lp.on('message', function(data) {
    data2 = JSON.parse(data);
    $("#"+data2['post_id']+" .w3-badge").html(data2['count']);
  });


  $(".submit_comment").click(function(e){
      submit_id = e.target.id
      post_id = submit_id.split("-")[1]
      comment = $("#comment-"+post_id+" .comment_box").val()

      $.post("/comment_on_post",
      {
        post_id: post_id,
        comment: comment,
      },
      function(data, status){
            //alert("Data: " + data + "Status: " + status);
            if(data['status'] ==  "fail"){
                alert("Please Try Again.")

            }else{
                $("#comment-"+post_id+" .panel-collapse").html(data)
            }
        })
  });

  $(".view_comments").click(function(e){
      submit_id = e.target.id
      post_id = submit_id.split("-")[1]

      $.post("/view_comments",
      {
        post_id: post_id,
      },
      function(data, status){
            //alert("Data: " + data + "Status: " + status);
            if(data['status'] ==  "fail"){
                alert("Please Try Again.")

            }else{
                $("#comment-"+post_id+" .panel-collapse").html(data)
            }
        })
  });






});


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

