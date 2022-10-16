import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

const SESSION_COOKIE_NAME = "scatter-login-session";

function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function eraseCookie(name) {
  document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});

if (params.address) {
  var address = `http://${params.address}` + "/game";
} else {
  var address = window.location.origin.replace(/\/+$/, "") + "/game";
}



var session = getCookie(SESSION_COOKIE_NAME);

class LoginForm extends React.Component {
  render() {
    return <div>
      <input type="password" id="password" />
      <button onClick={() => {
        let text = document.getElementById("password").value;
        fetch(`${address}/api/login`, {
          method: "POST",
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }, body: JSON.stringify({ passphrase: text })
        })
          .then(response => response.json()).then(
            (data) => {
              if (data.session !== undefined) {
                session = data.session;
                setCookie(SESSION_COOKIE_NAME, data.session, 1);
                window.location.reload();
              }

            }
          )
      }}>login</button>
    </div>
  }
}

class LogoutButton extends React.Component {
  render() {
    return <button onClick={
      () => {
        fetch(`${address}/api/logout`, {
          method: "POST",
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ "session": session })
        });
        session = null;
        eraseCookie(SESSION_COOKIE_NAME);
        window.location.reload();
      }
    } className="adminButton">logout</button>
  }
}



class NextButton extends React.Component {
  render() {
    return <button
      onClick={() => {
        fetch(`${address}/api/admin/next`, {
          method: "POST",
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ "session": session })
        });
      }}
      className="adminButton"
    >next</button>
  }
}

class ReloadButton extends React.Component {
  render() {
    return <button onClick={() => {
      fetch(`${address}/api/admin/reload`, {
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "session": session })
      }).then(data => data.json()).then(msg => alert(JSON.stringify(msg)));
    }} className="adminButton">reload</button>
  }
}

class AdminPanel extends React.Component {
  render() {
    return (<div>
      <NextButton /> <ReloadButton /> <LogoutButton />
    </div>);
  }
}

class QuestionField extends React.Component {
  render() {
    return (<div className='question-area'>
      <div className='question'>{this.props.question}</div>
    </div>);
  }
}

class LetterField extends React.Component {
  render() {
    return (<div className='letter-area'>
      <div className='letter'>{this.props.letter}</div>
    </div>)
  }
}

class GameStateDisplay extends React.Component {
  render() {
    return <div><div className='card'>
      <QuestionField question={this.props.data.question} />
      <LetterField letter={this.props.data.letter} />
    </div> {this.props.data.cards_left}</div>
  }
}

class Application extends React.Component {
  render() {
    let admin_part = null;
    if (session !== null) {
      admin_part = <div><AdminPanel /></div>
    } else {
      admin_part = (<div>
        <LoginForm />
      </div>)
    }
    return (
      <div>
        {admin_part}
        <GameStateDisplay data={this.props.data} />
      </div>)
  }
}





fetch(`${address}/api/state`).then(resp => resp.json()).then(data => {
  ReactDOM.render(
    <Application data={data} />,
    document.getElementById('root')
  );
}

)

var socket = null;
var attempts = 0;

function setup_socket() {
  let sock_addr = address.replace("http", "ws");
  let socket = new WebSocket(`${sock_addr}/ws`);

  socket.onmessage = function (event) {
    let data = JSON.parse(event.data);
    if (data == "heartbeat") {
      socket.send("Iamfine")
    } else {
      ReactDOM.render(
        <Application data={data} />,
        document.getElementById('root')
      );
    }

  }

  return socket;
}

socket = setup_socket();





function tick() {

  function draw_world(response) {
    response.then(response => response.json()).then(
      data => {
        ReactDOM.render(
          <Application data={data} />,
          document.getElementById('root')
        );
      });
  }

  draw_world(fetch(`${address}/api/state`));
  setTimeout(() => requestAnimationFrame(tick), 500)

}

//tick()