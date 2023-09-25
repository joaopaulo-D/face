const socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function () {
  console.log('Conectado ao servidor WebSocket');
});

socket.on('message', function (data) {
  const message = document.getElementById('message');
  message.innerHTML = data.message
});