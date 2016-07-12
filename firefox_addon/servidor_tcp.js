/*Servidor TCP para firefox*/
var { Cu } = require("chrome");
let { TCPServerSocket } = Cu.import("resource://gre/modules/Services.jsm", {});

var socket_escuchador = new TCPServerSocket(9000);

socket_escuchador.onconnect = function(evento){
                                console.log("conexion SEND:S pre");
                                evento.socket.send("caca");
                                console.log("conexion SEND:S pos");
                                evento.socket.ondata = function(evento){
                                                    console.log("data recivida: ", evento.data);
                                                }
                            }
socket_escuchador.onerror = function(evento) {
    console.log('port error!');
    console.log(evento.data)
}
