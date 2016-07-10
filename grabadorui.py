from threading import Thread
import kivy
from pywinvolume.volume_controller import KeyVolumeController

from grabador import Grabador
from widgetsbasicos import *

kivy.require("1.9.0")

from kivy.app import App

from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder

__author__ = "Daniel"

#TODO: CREAR SELECTOR DE FORMATO DE ARCHIVO
Builder.load_file("grabadorui.kv")

SPEAKERS_FRIENDLY_NAME = "Altavoz/Auricular (Realtek High Definition Audio)"

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
        if state == "normal":
            self.grabador.guardar = False
        elif state == "down":
            self.grabador.guardar = True

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