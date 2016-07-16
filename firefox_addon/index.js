/*Add-On creado para comunicar el cambio de nombre/video/titulo al grabador.ç
Como funciona:
 El add-on actua como servidor TCP para comunicarse con el grabador
 El grabador solicitara la conexión a firefox. Firefox le responde con una
 lista de las pestañas de youtube abiertas CON REPRODUCCION ACTIVA (es decir la
 pagina de un video) con sus correspondientes ID.
 El grabador responde con el ID de la pestaña de youtube elegida a monitorear.
 Firefox le responde cada vez que el titulo cambie (ES NECESARIO que le responda con
 el nombre de pestaña actual porque puede que haya pasado mucho tiempo
 desde que el grabador recivio los datos).*/
ACTUAL_NAME = ""

/*require("sdk/ui/button/action").ActionButton({
  id: "list-tabs",
  label: "List Tabs",
  icon: "./icon-16.png",
  onClick: listTabs
});*/

/*while (true)
  console.log("hola");*/
/*const tabs = require("sdk/tabs");
const {viewFor} = require('sdk/view/core');
const {modelFor} = require('sdk/model/core');
const {getBrowserForTab, getTabForContentWindow} = require("sdk/tabs/utils");*/
const {Ci, Cu} = require("chrome");
/*Cu.import("resource://gre/modules/XPCOMUtils.jsm", this);*/
Cu.import("resource://gre/modules/Timer.jsm");
var { TextEncoder, TextDecoder } = Cu.import("resource://gre/modules/Services.jsm");


//Crear servidor TCP

let { TCPServerSocket } = Cu.import("resource://gre/modules/Services.jsm", {});

const PORT = 9000;

var server = new TCPServerSocket(PORT, {binaryType:"arraybuffer"}, -1);
var to_cliente;

server.onconnect = function (event){
                        console.log("Conexión iniciada");
                        to_cliente = event.socket;
                        var encoded_data = new TextEncoder("utf-8").encode(listTabs());
                        console.log("encoded_data: ", encoded_data);
                        to_cliente.send(encoded_data.buffer);
                        to_cliente.ondata = function(event){
                                                monitorearTab(event.data);
                                            };
                   }

function monitorearTab(tabID){
    console.log("data recivida:", tabID )
    tabID = new TextDecoder("utf-8").decode(tabID);
    const {modelFor} = require('sdk/model/core');

    console.log("ID de pestaña:", tabID);
    var tab;
    var tabs = require("sdk/tabs");
    var tabUtils = require("sdk/tabs/utils");

    tab = tabUtils.getTabForId(tabID);
    tab = modelFor(tab);
    console.log("Pestaña recuperada: ", tab);
    ACTUAL_NAME = tab.title.slice(0, tab.title.length - 10);
    console.log("Nombre de pestaña:", ACTUAL_NAME);
    var encoded_data = new TextEncoder("utf-8").encode(ACTUAL_NAME);
    to_cliente.send(encoded_data.buffer);
    setTitleTimer(tab);
}

function listTabs() {
  var is_youtube_video = /^https:\/\/www\.youtube\.com\/watch.*/;
  var tabs = require("sdk/tabs");
  var jsonPestañas = {};
  for (let tab of tabs){
    //console.log(tab.url);
    if (is_youtube_video.test(tab.url)){
      console.log("Pestaña:", tab.id, tab.title);
      jsonPestañas[tab.id] = tab.title;
      //setChangeTabNameListener(tab);
      //var lowLevel = viewFor(tab);
      //var browser = getBrowserForTab(lowLevel);
      //browser.addProgressListener(progressListener);
    }
  }
  console.log("El Json es: ",jsonPestañas,JSON.stringify(jsonPestañas));
  return JSON.stringify(jsonPestañas);
}


function setTitleTimer(tab){
    let intervalID = setInterval(
        function() {
            NEW_NAME = tab.title.slice(0, tab.title.length - 10);
            if (ACTUAL_NAME != NEW_NAME){
                ACTUAL_NAME = NEW_NAME
                console.log("Cambio de nombre a:", ACTUAL_NAME);
                to_cliente.send((new TextEncoder("utf-8").encode(ACTUAL_NAME)).buffer);
                console.log("Cambio enviado con exito");
            }
        },
    50);
}

/*function setChangeTabNameListener(tab){
    tab.on("pageshow", function (){console.log("pageshowed")});
    tab.on("activate", function() {console.log("activated")});
    tab.on("deactivate", function() {console.log("deactivated")});
    tab.on("close", function (){console.log("closed")});
    tab.on("ready", function (){console.log("ready")});
    tab.on("load", function (){console.log("load")});
}*/


/*var progressListener = {
QueryInterface: XPCOMUtils.generateQI([Ci.nsIWebProgressListener, Ci.nsISupportsWeakReference]),
    onProgressChange: function(aProgress, aRequest, aURI, aFlags)   {
        var highLevel= modelFor(getTabForContentWindow(aProgress.DOMWindow));
        console.log("onLocationChange ", highLevel.title, "flags", aFlags);
    }
};*/

/*tabs.on('open', function(newTab) {
    var lowLevel = viewFor(newTab);
    var browser = getBrowserForTab(lowLevel);
    browser.addProgressListener(progressListener);
});
*/