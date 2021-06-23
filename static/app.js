
$(document).ready(function(){
var site_url = 'http://127.0.0.1:5000'
var socket_cp = io.connect(site_url+'/create_post');

  $("#post").click(function(e){
    socket_cp.send($("#content_post").html());
    $("#content_post").html("");
  });
  socket_cp.on('message', function(data) {
     $("#post_body").prepend(data)
  });

var socket_lp = io.connect(site_url+'/like_post');

  $(".like_post").click(function(e){
    post_id = e.target.id
    request_data = {"post_id": post_id}
    socket_lp.emit('like_event', request_data);

  });
  socket_lp.on('like_response', function(data) {
    $("#"+data['post_id']+" .w3-badge").html(data['count']);
  });

var socket_cop = io.connect(site_url+'/comment_on_post');

  $(".submit_comment").click(function(e){
    submit_id = e.target.id
    post_id = submit_id.split("-")[1]
    comment = $("#comment-"+post_id+" .comment_box").val()
    request_data = {"post_id": post_id, "comment": comment}
    socket_cop.emit('comment_event', request_data);
  });

  socket_cop.on('comments_response', function(data) {
  console.log(data)
     $("#comment-"+data['post_id']+" .panel-collapse").html(data['comments']);
     $("#comment-"+data['post_id']+" .comment_box").val("");
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

