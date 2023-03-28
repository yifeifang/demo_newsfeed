function init()
{
  console.log("init....");
  
  console.log("register enter event");
  var input = document.getElementById("user_input");
  // Execute a function when the user releases a key on the keyboard
  input.addEventListener("keydown", function(event) {  
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
      // Cancel the default action, if needed
      event.preventDefault();
      // Trigger the button element with a click
     document.getElementById("user_send").click();
    }
  });
  
  console.log("init finished");
}

function robot_reply(reply)
{
  draw_bubble(reply, "bubble_l");
}

function user_send()
{ 
  const text_input = document.getElementById("user_input").value;
  const current_user = document.getElementById("current_user").innerText;
  draw_bubble(text_input, "bubble_r");
  
  const formData = new FormData();
  formData.append("content", text_input);
  formData.append("user", current_user);
  send_request("post", "http://localhost:5000/v1/me/feed", formData, null)
}

function render_feed(responseText)
{
  console.log(responseText);
  var response = JSON.parse(responseText);
  var content = response.content;
  for (var i = 0; i < content.length; i++) {
    console.log(content[i]);
    draw_bubble(content[i][0] + ": " + content[i][1], "bubble_l");
  }
}

function reterive_feed()
{
  const text_input = document.getElementById("user_id").value;
  const current_user = document.getElementById("current_user").innerText;
  send_request("get", "http://localhost:5000/v1/me/feed?user=" + current_user, null, render_feed);
}

function create_user()
{
  const text_input = document.getElementById("user_id").value;
  const current_user = document.getElementById("current_user"); 
  current_user.innerText = text_input;
  send_request("get", "http://localhost:5000/users/create?name=" + text_input, null, null)
}

function add_friend()
{
  const text_input = document.getElementById("user_id").value;
  const current_user = document.getElementById("current_user");
  send_request("get", "http://localhost:5000/users/" + current_user.innerText +"/friends/add?friend=" + text_input, null, null);
  
  const newDiv = document.createElement("div"); 
  newDiv.innerHTML = text_input;
  const parentDIV = document.getElementById("friend"); 
  parentDIV.appendChild(newDiv);
}

function draw_bubble(text, bubble_side)
{
  const br = document.createElement('br');
  const newDiv = document.createElement("div"); 
  newDiv.className = bubble_side;
  
  if(text)
  {
    newDiv.innerHTML = text;
  }
  else
  {
    return false;
  }

  // add the newly created element and its content into the DOM 
  const parentDIV = document.getElementById("chat"); 
  const currentDiv = document.getElementById("chatend"); 
  parentDIV.insertBefore(br, currentDiv); 
  parentDIV.insertBefore(newDiv, currentDiv);
  
  document.getElementById("user_input").value = "";
  updateScroll();
  
  return true;
}

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function updateScroll(){
    var element = document.getElementById("chat");
    element.scrollTop = element.scrollHeight;
}

function send_request(method, URL, data, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.open(method, URL);
  if(method.toUpperCase() == "POST")
  {
    // xhttp.setRequestHeader("Content-Type", "application/form-data");
    // xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(data);
  }
  else
  {
    xhttp.send();
  }
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      // console.log(this.responseText);
      callback(this.responseText);
    };
  };
}

