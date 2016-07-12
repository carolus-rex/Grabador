/*Add-On creado para comunicar el cambio de nombre/video/titulo al grabador.ç
Como funciona:
 El add-on actua como servidor TCP para comunicarse con el grabador
 El grabador solicitara la conexión a firefox. Firefox le responde con una
 lista de las pestañas de youtube abiertas CON REPRODUCCION ACTIVA (es decir la
 pagina de un video) con sus correspondientes ID.
 El grabador responde con el ID de la pestaña de youtube elegida a monitorear.
 Firefox le responde cada vez que el titulo cambie (no es necesario que le responda con
 el nombre de pestaña actual porque se supone que el grabador ya lo cogió).*/
ACTUAL_NAME = ""

require("sdk/ui/button/action").ActionButton({
  id: "list-tabs",
  label: "List Tabs",
  icon: "./icon-16.png",
  onClick: listTabs
});

/*while (true)
  console.log("hola");*/
/*const tabs = require("sdk/tabs");
const {viewFor} = require('sdk/view/core');
const {modelFor} = require('sdk/model/core');
const {getBrowserForTab, getTabForContentWindow} = require("sdk/tabs/utils");*/
const {Ci, Cu} = require("chrome");
/*Cu.import("resource://gre/modules/XPCOMUtils.jsm", this);*/
Cu.import("resource://gre/modules/Timer.jsm");


function listTabs() {
  var is_youtube_video = /^https:\/\/www\.youtube\.com\/watch.*/;
  var tabs = require("sdk/tabs");
  for (let tab of tabs){
    //console.log(tab.url);
    if (is_youtube_video.test(tab.url)){
      ACTUAL_NAME = tab.title.slice(0, tab.title.length - 10);
      console.log(ACTUAL_NAME);
      setTitleTimer(tab);
      //setChangeTabNameListener(tab);
      //var lowLevel = viewFor(tab);
      //var browser = getBrowserForTab(lowLevel);
      //browser.addProgressListener(progressListener);
    }
  }
}


function setTitleTimer(tab){
    let intervalID = setInterval(
        function() {
            NEW_NAME = tab.title.slice(0, tab.title.length - 10);
            if (ACTUAL_NAME != NEW_NAME){
                ACTUAL_NAME = NEW_NAME
                console.log(ACTUAL_NAME);
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