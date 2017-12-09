from time import sleep, strftime

import lame
import os

from guardadores.base import GuardadorBase

__author__ = "Daniel"


class Guardador(GuardadorBase):
    def run(self):
        sound_pcm = b""
        sound_chunks = 0
        while True:
            if self._iniciado_sin_grabador:
                sleep(0.1)
                continue
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
                            if self.archivo is None or self.archivo.closed:
                                self.crear_nuevo_archivo()
                            self.archivo.writeframes(sound)
                        else:
                            if not self._silencio:
                                print("Grabación Terminada")
                                self._silencio = True
                                self.archivo.close()
                        sound_chunks = 0
                        sound_pcm = b""
                else:
                    for key, value in data.items():
                        self.interpretar_orden(key, value)
                    sound_chunks = 0
                    sound_pcm = b""
                    self.archivo.close()
            else:
                sleep((1/self.grabador.rate) * self.grabador.CHUNK)

    def crear_nuevo_archivo(self):
        print("Crear nuevo archivo?")
        try:
            if self.archivo.getduration() < self.archivo_min_duration:
                # Si el archivo es muy corto reusa el existente
                self.archivo = lame.open(self.archivo_name, "wb")
                print("No")
            else:
                # Crea un nuevo archivo
                self.archivo_name = os.path.join(self.DATA_PATH, strftime("%y-%m-%d--%H-%M-%S") + ".mp3")
                self.archivo = lame.open(self.archivo_name, "xb")
                print("Si " + self.archivo_name)
        except AttributeError:
            # Crea el primer archivo
            self.archivo_name = os.path.join(self.DATA_PATH, strftime("%y-%m-%d--%H-%M-%S") + ".mp3")
            self.archivo = lame.open(self.archivo_name, "wb")
            print("Si " + self.archivo_name)
        self.archivo.setframerate(self.rate)
        self.archivo.setsampwidth(self.grabador.p.get_sample_size(self.formatM) * 8) #Usa este cuando sea mp3
        self.archivo.setnchannels(self.channels)
