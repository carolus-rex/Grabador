from time import sleep

import numpy as np
import pyaudio

from guardadores.mp3 import Guardador

__author__ = "Daniel"


class Grabador(object):
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.CHUNK = 1024
        self.format_in_bits = 16
        self.channels = 2
        self.rate = 48000
        self.parlantes = self.p.get_default_input_device_info()["index"]
        self.fuente = self.p.get_default_output_device_info()["index"]
        self.stream = None
        self.crear_stream()
        self.data_chunks = []
        self.guardar = False
        self.cambios = {}
        self.guardador = Guardador(self)
        self.guardador.setName("Guardador")
        self._bloquear_data_chunks = False

    def get_inputs(self):
        values = []
        index = 0
        try:
            while True:
                device = self.p.get_device_info_by_index(index)
                if device["maxInputChannels"] > 0:
                    values.append(device["name"])
                    print(device["index"])
                index += 1
        except OSError:
            return values

    def get_outputs(self):
        values = []
        index = 0
        try:
            while True:
                device = self.p.get_device_info_by_index(index)
                if device["maxOutputChannels"] > 0:
                    values.append(device["name"])
                    print(device["index"])
                index += 1
        except OSError:
            return values

    def iniciar(self):
        while True:
            sonido = self.stream.read(self.CHUNK)
            if self.format_in_bits not in (16, 24):
                sonido = self.simular_formato(sonido)
            self.stream.write(sonido)
            if self.guardar and not self._bloquear_data_chunks:
                self.data_chunks.append(sonido)
            if self.cambios:
                tx_cambios = {}
                for key, value in self.cambios.items():
                    if key == "output":
                        self.parlantes = value
                    elif key == "input":
                        self.fuente = value
                    elif key == "rate":
                        self.rate = value
                        tx_cambios[key] = value
                    elif key == "channels":
                        self.channels = value
                        tx_cambios[key] = value
                    elif key == "format_in_bits":
                        self.format_in_bits = value
                        tx_cambios[key] = pyaudio.paInt16 if 1 <= value <= 16 else pyaudio.paInt32
                    elif key == "cerrar":
                        tx_cambios[key] = value
                self.cambios.clear()
                self.stream.close()
                self.crear_stream()
                if tx_cambios and not self._bloquear_data_chunks:
                    self.data_chunks.append(tx_cambios)
            #sleep(self.CHUNK * (1/self.rate))

    def crear_stream(self):
        #self.stream.close()
        if 1 <= self.format_in_bits <= 16:
            pyaudio_format = pyaudio.paInt16
        else:
            pyaudio_format = pyaudio.paInt32
        self.stream = self.p.open(rate=self.rate,
                                  channels=self.channels,
                                  format=pyaudio_format,
                                  input=True,
                                  output=True,
                                  input_device_index=self.parlantes,
                                  output_device_index=self.fuente)

    def simular_formato(self, sound):
        #TODO: Arregla este metodo
        if 1 <= self.format_in_bits <= 16:
            nptype = np.int16
            factor_normalizador = 32768

        else:
            nptype = np.int32
            factor_normalizador = 2147483648
        factor_escalador = 1 << (self.format_in_bits - 1)
        factor_escalador_real = 1 << (self.format_in_bits)
        # Convierto el stream de bytes a un array numpy
        arr_sound = np.frombuffer(sound, dtype=nptype).reshape((-1, self.channels))
        # Colocar a 0
        data_offset_0 = arr_sound + factor_normalizador
        data_voltaje = (data_offset_0 / (factor_normalizador * 2)) * 5 # Datos a 5 voltios
        data_trans_offset_0 = (data_voltaje / 5) * factor_escalador_real # Datos a escala maxima
        data_fake_offset_0 = (data_trans_offset_0 // 1) / factor_escalador_real #Datos a escala truncados(codificados) y luego a escala 1
        data_fake_offset_0_mode = data_fake_offset_0 * factor_normalizador * 2 # Datos a escala inicial
        data_fake = data_fake_offset_0_mode - factor_normalizador # Datos con offset al medio
        #data = (((((arr_sound / factor_normalizador) * factor_escalador) // 1) / factor_escalador) * factor_normalizador).astype(nptype, copy=False)
        data = (data_fake).astype(nptype, copy=False)
        return data.tobytes()

    def cambiar_guardador(self, guardador):
        # El grabador manipulara directamente los valores del guardador
        # para evitar estupideces. Quiza esto sea una estupidez
        self._bloquear_data_chunks = True
        while self.data_chunks:
            sleep(0.1)
        print("Grabador vacio data")
        # Me aseguro de que todos los datos registrados se graben
        try:
            if not self.guardador.archivo.closed:
                self.guardador.archivo.close()
        except AttributeError:
            pass
        #Esto causara un crash Nonetype. Es feo, pero es facil de implementar
        self.guardador.grabador = None
        #sleep(5)
        guardador.channels = self.channels
        guardador.CHUNK = self.CHUNK
        guardador.formatM = pyaudio.paInt16 if 1 <= self.format_in_bits <= 16 else pyaudio.paInt32
        guardador.rate = self.rate
        guardador.agregar_grabador(self)
        self.guardador = guardador
        self._bloquear_data_chunks = False

if __name__ == "__main__":
    Grabador().iniciar()
