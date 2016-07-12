/*Cliente TCP para firefox*/

var { Cu } = require("chrome");
//var { TextEncoder, TextDecoder } = Cu.import("resource://gre/modules/Services.jsm");


function createTCPSocket(location, port, options) {
  // Starting with FF43, TCPSocket is now exposed via WebIDL
  let { TCPSocket } = Cu.import("resource://gre/modules/Services.jsm", {});
  if (TCPSocket) {
    console.log("if worked ************", TCPSocket)
    return new TCPSocket(location, port, options);
    //new_sock = new TCPSocket(location, port, options);
    //console.log(new_sock)º
    //var data = Uint8Array.from("hola");
    //var data = new StringView("hola");
    //console.log("data", data)
    /*new_sock.send(data);
    console.log("data enviada");*/
  }
  let scope = Cu.Sandbox(Services.scriptSecurityManager.getSystemPrincipal());
  scope.DOMError = Cu.import("resource://gre/modules/Services.jsm", {}).DOMError;
  Services.scriptloader.loadSubScript("resource://gre/components/TCPSocket.js", scope);
  scope.TCPSocket.prototype.initWindowless = function () true;
  let socket = new scope.TCPSocket();
  return socket.open(location, port, options);
}
//var uint8array = new TextEncoder("utf-8").encode("hola");
/*var data = Uint8Array.from("hola");*/
/*console.log("data", uint8array);
console.log("tipo", typeof uint8array);
var data = Array.from("hola");
console.log("data array", data);
console.log("tipo", typeof data);*/


socket = createTCPSocket("localhost", 2500);
socket.ondata = function (event) {
    if (typeof event.data === 'string') {
        console.log('Get a string: ' + event.data);
    } else {
        console.log('Get a Uint8Array');
    }
}
//var uint8array = new TextEncoder("utf-8").encode("hola");
/*if (socket.send === undefined)
    console.log("CACA, EL METODO SEND NO ESTA DEFINIDO D:")
else
    console.log("METODO SEND DEFINIDO", socket.send)
var data = Array.from("hola");*/

//socket.send(data);
require("sdk/ui/button/action").ActionButton({
  id: "list-tabs",
  label: "List Tabs",
  icon: "./icon-16.png",
  onClick: sender
});

function sender(){
  socket.send("caca")
}
/*socket = createTCPSocket("localhost", 2500, {binaryType:"arraybuffer"});*/
/*
var data = Uint8Array.from("hola");
console.log(data);
socket.send(data);
*/
