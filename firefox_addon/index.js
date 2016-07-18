/*Add-On creado para comunicar el cambio de nombre/video/titulo al grabador.
Como funciona:
 El add-on actúa como servidor TCP para comunicarse con el grabador.
 El grabador solicitará la conexión a firefox. Firefox le responde con una
 lista de las pestañas de youtube abiertas CON REPRODUCCION ACTIVA (es decir la
 página de un video) con sus correspondientes ID.
 El grabador responde con el ID de la pestaña de youtube elegida a monitorear.
 Firefox le responde cada vez que el título cambie (ES NECESARIO que le responda con
 el nombre de pestaña actual porque puede que haya pasado mucho tiempo
 desde que el grabador recivio los datos).*/

ACTUAL_NAME = ""

const {modelFor} = require('sdk/model/core');
const {Ci, Cu} = require("chrome");
Cu.import("resource://gre/modules/Timer.jsm");
var { TextEncoder, TextDecoder } = Cu.import("resource://gre/modules/Services.jsm");
var tabUtils = require("sdk/tabs/utils");
var TABS = require("sdk/tabs");
let { TCPServerSocket } = Cu.import("resource://gre/modules/Services.jsm", {});

var TO_CLIENTE;
var TIMER_ACTUAL;
const IS_YOUTUBE_VIDEO = /^https:\/\/www\.youtube\.com\/watch.*/;
var ENCODER = new TextEncoder("utf-8");
var DECODER = new TextDecoder("utf-8");

//Crear servidor TCP

const PORT = 9000;
var SERVER = new TCPServerSocket(PORT, {binaryType:"arraybuffer"}, -1);


SERVER.onconnect = function (event){
                       console.log("Conexión iniciada");
                       TO_CLIENTE = event.socket;
                       var encoded_data = encode(listTabs());
                       /*console.log("encoded_data: ", encoded_data);*/
                       TO_CLIENTE.send(encoded_data);
                       TO_CLIENTE.ondata = function(event){
                                               monitorearTab(event.data);
                                           };
                   }


function monitorearTab(tabID){
    console.log("data recivida:", tabID )
    tabID = decode(tabID);
    console.log("ID de pestaña: ", tabID);

    var tab;
    tab = tabUtils.getTabForId(tabID);
    tab = modelFor(tab);
    console.log("Pestaña recuperada: ", tab);

    ACTUAL_NAME = tab.title.slice(0, tab.title.length - 10);
    console.log("Nombre de pestaña:", ACTUAL_NAME);
    var encoded_data = encode(ACTUAL_NAME);
    TO_CLIENTE.send(encoded_data);

    clearInterval(TIMER_ACTUAL);
    setTitleTimer(tab);
}


function listTabs(){
    var jsonPestañas = {};
    for (let tab of TABS){
    //console.log(tab.url);
        if (IS_YOUTUBE_VIDEO.test(tab.url)){
            console.log("Pestaña:", tab.id, tab.title);
            jsonPestañas[tab.id] = tab.title;
        }
    }
    var pestañasString = JSON.stringify(jsonPestañas);
    console.log("El Json es: ", pestañasString);
    return pestañasString;
}


function setTitleTimer(tab){
    TIMER_ACTUAL = setInterval(
        function(){
            NEW_NAME = tab.title.slice(0, tab.title.length - 10);
            if (ACTUAL_NAME != NEW_NAME){
            ACTUAL_NAME = NEW_NAME
            console.log("Cambio de nombre a:", ACTUAL_NAME);
            TO_CLIENTE.send(encode(ACTUAL_NAME));
            console.log("Cambio enviado con éxito");
            }
        },
        50);
}


function encode(string){
    /*
    Devuelve un BUFFER no un Uint8Array.
    Por algún motivo TCPServerSocket.send() utiliza buffers en lugar de Uin8Arrays.
    La documentación dice que si usa Uint8Arrays pero cuando lo pruebo no funciona.
    Ten esto en cuenta porque puede que en futuro cambie.
    */
    return ENCODER.encode(string).buffer;
    console.log("data encoded", buffer)
}


function decode(Uint8Array){
    return DECODER.decode(string);
}
