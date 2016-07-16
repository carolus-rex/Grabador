from functools import partial
from threading import Thread
from time import sleep

import kivy
from kivy.uix.togglebutton import ToggleButton
from pywinvolume.volume_controller import KeyVolumeController

from grabador import Grabador
from guardadores.youtube import GuardadorMP3
from widgetsbasicos import *

kivy.require("1.9.0")

from kivy.app import App

from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder

__author__ = "Daniel"

#TODO: CREAR SELECTOR DE FORMATO DE ARCHIVO
Builder.load_file("grabadorui.kv")

SPEAKERS_FRIENDLY_NAME = "Altavoz/Auricular (Realtek High Definition Audio)"

class YoutubePopup(Popup):
    grabadorui = ObjectProperty()

class AskToggleButton(ToggleButton):
    check_premission = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.check_permission():
            super(AskToggleButton, self).on_touch_down(touch)
        else:
            return False


class GrabadorUi(BoxLayout):
    def __init__(self, **kwargs):
        self.grabador = Grabador()
        Thread(target=self.grabador.iniciar, name="grabador").start()

        self.key_volume_controller = KeyVolumeController(SPEAKERS_FRIENDLY_NAME)
        self.key_volume_controller.start()

        super(GrabadorUi, self).__init__(**kwargs)
        self.ids.inputs.text = self.grabador.p.get_default_input_device_info()["name"]
        self.ids.inputs.values = self.grabador.get_inputs()

        self.ids.outputs.text = self.grabador.p.get_default_output_device_info()["name"]
        self.ids.outputs.values = self.grabador.get_outputs()
        self._guardador = None
        self._tab_selected = False

    def search_device(self, name):
        index = 0
        try:
            while True:
                device = self.grabador.p.get_device_info_by_index(index)
                if device["name"] == name:
                    return device["index"]
                index += 1
        except OSError:
            print("esto no debería ocurrir")

    def change_input(self, wid, name):
        device = self.search_device(name)
        self.grabador.cambios["input"] = device

    def change_output(self, wid, name):
        device = self.search_device(name)
        self.grabador.cambios["output"] = device

    def toggle_grabar(self, wid, state):
        if state == "normal": # Deja de grabar
            # MUY IMPORTANTE QUE ESTA LINEA SE QUEDE AHI
            # CUANDO CAMBIA DE ESTADO pausartoggle a normal LE ORDENA AL GRABADOR
            # QUE EMPIECE A GRABAR(self.grabador.guardar = True)
            #  Y ESO ES LO QUE NO QUEREMOS QUE OCURRA
            # LA SIGUIENTE LINEA HACE QUE DEJE DE GRABAR (self.grabador.guardar = False)
            # ES POR ESO QUE NO DEBE MOVERSE
            self.ids.grabartoggle.text = "Grabar"
            self.ids.pausartoggle.state = "normal"
            self.grabador.guardar = False
            #self.grabador.cambios["cerrar"] = True        #Puedo cerrar el archivo asi
            self.grabador.guardador.crear_nuevo_archivo()  #Tambien puedo hacerlo asi, no me convence mucho
        elif state == "down": # Empieza a grabar
            self.ids.grabartoggle.text = "Detener"
            self.grabador.guardar = True
            #self.ids.pausartoggle.state = "normal"

    def permitir_pausartoggle(self):
        if self.ids.grabartoggle.state == "down":
            return True
        elif self.ids.grabartoggle.state == "normal":
            return False

    def toggle_pausar(self, wid, state):
        """Indica al grabador que deje de enviar data a la lista para guardar."""
        if state == "normal": # Empieza a mandar datos (no está pausado)
            self.ids.pausartoggle.text = "Pausar"
            self.grabador.guardar = True
        elif state == "down": # Deja de mandar datos (está pausado)
            self.ids.pausartoggle.text = "Pausado"
            self.grabador.guardar = False

    def toggle_youtube(self, wid, state):
        if state == "down":
            YoutubePopup(grabadorui=self).open()

    def crear_guardador_youtube(self, wid, *args):
        self.grabador.guardar = False
        guardador = GuardadorMP3(self.grabador)
        while True:
            data = guardador.youtube.get_tabs()
            print("Esta es la data del bucle: ", data)
            if data is not None:
                break
            # print("No hay tabs...")
            sleep(0.001) # Esto es un asco, lo se, pero no se me ocurre nada mas que sea facil de implementar
        #data = guardador.youtube.get_tabs()
        if len(data) == 1:
            id = tuple(data.keys())[0]
            print("solo tengo una data, voy a enviar esta id : ", id)
            #print("Increiblemente mi data ahora es esto: ", data)
            #Solo tengo una opcin posible, asi que la elijo automaticamente sin preguntarle al usuario
            self.elegir_tab(wid,
                            id,
                            guardador)
            return
        for id, title in data:
            button = Button(text=title,on_press=partial(self.elegir_tab, wid, id, guardador))
            self.ids.vistascroll.add_cuadro(button)

    def quitar_popup(self, wid, *args):
        if not self._tab_selected:
            self._guardador.terminar()
        self._tab_selected = False
        #wid.ids.vista_scroll.borrar_cuadros()

    def elegir_tab(self, wid, id, guardador):
        #TODO: Implementar en el Grabador un mejor metodo para hacer el cambio de Guardador
        print("Tab elegida")
        while self.grabador.data_chunks:
            sleep(0.03)
        print("Grabador vacio data")
        self.grabador.guardador.grabador = None
        self.grabador.guardador = guardador
        print("Tab id a elegir: ", id)
        guardador.youtube.set_tab(id)
        #print("El grabador es: ", guardador.grabador)
        #sleep(5)
        self.grabador.guardar = True
        #TODO: Fix the race condition. se produce porque el nombre y la autorizacion para que el grabador guarde ocurren casi al mismo tiempo
        self._tab_selected = True
        wid.dismiss()

    def change_rate(self, wid, rate):
        if len(rate) > 3 and (int(rate) != 0):
            self.grabador.cambios["rate"] = int(rate)

    def change_channels(self, wid, channels):
        if len(channels) == 1:
            self.grabador.cambios["channels"] = int(channels)

    def change_format(self, wid, format_in_bits):
        if 1 <= len(format_in_bits) <= 2:
            self.grabador.cambios["format_in_bits"] = int(format_in_bits)

    def change_min_time(self, wid, seconds):
        try:
            if int(seconds) > 0:
                self.grabador.guardador.definir_tiempo_de_grabacion_minimo(int(seconds))
        except ValueError:
            pass


class GrabadorApp(App):
    def build(self):
        return GrabadorUi()


if __name__ == "__main__":
    GrabadorApp().run()