socket = io()

const slide = () => {
  const ul = document.getElementById('logline');
  ul.scrollTop = ul.scrollHeight;
}

const bago = ({ message, label }) => {
  if (typeof message == "string"){
    let $hasLabel = label?.text ? `<span style="color: ${label?.color ?? "#6167e9"}"><b>${label.text} ⟩⟩ </b></span>` : ''
    $('#logline').append($("<li>").html(`${$hasLabel}${message}`))
    slide()
  }
}

const panel = (data) => {
  if (!data?.type) {
    $("#logline").append($("<li>").addClass('info').html(`
      <div class="head">
        <p style="color:red><i class="fa-solid fa-bug"></i> <b>LOG</b></p>
      </div>
      <div class='data'>
        Missing 'type' data
      </div>
    `))
    slide()
    return
  }
  if (data.type === 'user'){
    const { name, uid, threadId, command } = data;
    $("#logline").append($("<li>").addClass("user").html(`
      <div class="head bg-dark">${name}</div>
      <div class="body">
        <span><b>UserID: </b>${uid}</span><br>
        <span><b>ThreadID: </b>${threadId}</span><br>
        <span class="command"><b>Command: </b>${command}</span>
      </div>
    `))
  }
  else if (data.type === 'info'){
    let { label, body, border } = data;
    const { color, text, icon } = label;
    let fa = icon?`<i class="${icon}"></i>`:''
    $("#logline").append($("<li>").addClass('info').css({"border": `1px solid ${border??'white'}`}).html(`
      <div class="head">
        <p style="color:${color??"white"}">${fa} <b>${text.toUpperCase()??"INFO"}</b></p>
      </div>
      <div class='data'>
        ${body.replace(/\n/g, '<br>').trim()}
      </div>
    `))
  }
  slide()
}

// get the new log
socket.on("log", (data) => {
  if (data?.message){
    bago({message:data.message,label:data.label})
  }
  else {
    panel(data)
  }
})

// get all logs
async function logs(session){
  try{
    const response = await fetch(`/api/logs/${session}`);
    const data = await response.json();
    panel({
      type: "info",
      border: "#4635B1",
      body: `<b>Name:</b> Christopher
      <b>Age:</b> 16
      <b>Gender:</b> Male
      <b>Github:</b> https://github.com/christhenoob13
      <b>Facebook:</b> https://facebook.com/christopher.jr.01
      `,
      label: {
        text: "DEVELOPER",
        color: "#074799",
        icon: "fa-solid fa-shield"
      }
    })
    bago({
      message: `Session <i>${session}</i>`,
      label: {
        text: "FLASK",
        color: "#FF9D3D"
      }
    })
    data.forEach(log => {
      if (log?.message){bago(log)}
      else{
        panel(log)
      }
    })
  }catch(error){
    bago({
      message: error,
      label: {
        text: "ERROR",
        color: "red"
      }
    })
  }
}

// clear log
$(document).ready(function(){
  $("#clear").click(function(){
    $("#logline").html("")
    socket.emit('clearLog', {})
  })
  
  $("#test").click(() => {
    
  })
})