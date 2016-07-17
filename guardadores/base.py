from threading import Thread

import numpy as np
import pyaudio

__author__ = "Daniel"


class GuardadorBase(Thread):
    def __init__(self, grabador):
        self.archivo_min_duration = 60
        self.grabador = grabador
        self.CHUNK = self.grabador.CHUNK
        self.formatM = pyaudio.paInt16 if 1 <= self.grabador.format_in_bits<= 16 else pyaudio.paInt32
        self.channels = self.grabador.channels
        self.rate = self.grabador.rate
        self.archivo = None
        self.archivo_name = None
        self.tamaño_chunk_ideal = 8192
        self.ruido_ambiente = 0.00028
        self._silencio = True
        super(GuardadorBase, self).__init__()
        self.start()

    def run(self):
        pass
        """sound_pcm = b""
        sound_chunks = 0
        while True:
            if self.grabador.data_chunks:
                data = self.grabador.data_chunks.pop(0)
                if isinstance(data, bytes):
                    sound_pcm += data
                    sound_chunks += 1
                    if sound_chunks * self.CHUNK >= self.tamaño_chunk_ideal:
                        sound = self.bytes_to_nparray(sound_pcm)
                        rms = self.calcular_rms(sound)
                        #sound = sound_pcm
                        #print(rms)
                        if rms > self.ruido_ambiente:
                            if self._silencio:
                                self._silencio = False
                                #self.crear_nuevo_archivo()
                            self.archivo.writeframes(sound)
                        else:
                            if not self._silencio:
                                print("Grabación Terminada")
                                self._silencio = True
                                self.crear_nuevo_archivo()
                        sound_chunks = 0
                        sound_pcm = b""
                else:
                    for key, value in data.items():
                        if key == "rate":
                            self.rate = value
                        elif key == "channels":
                            self.channels = value
                        elif key == "format_in_bits":
                            self.formatM = value
                    sound_chunks = 0
                    sound_pcm = b""
                    self.crear_nuevo_archivo()
            else:
                sleep((1/self.grabador.rate) * self.grabador.CHUNK)"""

    def interpretar_orden(self, orden, valor):
        # Si en algun momento se me ocurriese hacer un guardador con acciones
        # especificas, tendria que hacer que ejecute funciones en lugar de que
        # solamente modifique valores
        if orden == "rate":
            self.rate = valor
        elif orden == "channels":
            self.channels = valor
        elif orden == "format_in_bits":
            self.formatM = valor
        elif orden == "cerrar":
            # Crea un nuevo archivo y guarda lo hecho hasta ahora
            print("Orden de cerrar el archivo")
        else:
            print("Data tipo %s con valor %s no reconocida" %(orden, valor))

    def crear_nuevo_archivo(self):
        """print("Crear nuevo archivo?")
        try:
            self.archivo.close()
            if self.archivo.getduration() < self.archivo_min_duration:
                self.archivo = lame.open(self.archivo_name, "wb")
                print("No")
            else:
                self.archivo_name = "C:\\Users\\Administrador\\grabado\\" + strftime("%y-%m-%d--%H-%M-%S") + ".mp3"
                self.archivo = lame.open(self.archivo_name, "xb")
                print("Si " + self.archivo_name)
        except AttributeError:
            self.archivo_name = "C:\\Users\\Administrador\\grabado\\" + strftime("%y-%m-%d--%H-%M-%S") + ".mp3"
            self.archivo = lame.open(self.archivo_name, "wb")
            print("Si " + self.archivo_name)
        self.archivo.setframerate(self.rate)
        self.archivo.setsampwidth(self.grabador.p.get_sample_size(self.formatM) * 8) #Usa este cuando sea mp3
        self.archivo.setnchannels(self.channels)"""
        pass

    def bytes_to_nparray(self, data):
        if self.formatM == pyaudio.paInt16:
            nptype = np.int16
        elif self.formatM == pyaudio.paInt32:
            nptype = np.int32
        return np.frombuffer(data, dtype=nptype).reshape((-1, self.channels))

    def calcular_rms(self, sound):
        if self.formatM == pyaudio.paInt8:
            factor_normalizador = 128
        elif self.formatM == pyaudio.paInt16:
            factor_normalizador = 32768
        elif self.formatM == pyaudio.paInt24:
            factor_normalizador = 8388608
            raise NotImplementedError("Numpy no soporta formato de 24 bits/3 bytes")
        elif self.formatM == pyaudio.paInt32:
            factor_normalizador = 2147483648
        return np.sqrt(np.sum((sound / factor_normalizador) ** 2) / len(sound))

    def definir_tiempo_de_grabacion_minimo(self, segundos):
        self.archivo_min_duration = segundos
