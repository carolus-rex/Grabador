from time import sleep, strftime

import lame
from guardadores.base import GuardadorBase

__author__ = "Daniel"

class Guardador(GuardadorBase):
    def run(self):
        sound_pcm = b""
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
                        elif key == "cerrar":
                            # Crea un nuevo archivo y guarda todo lo hecho hasta ahora
                            pass
                        else:
                            print("Data tipo %s con valor %s no reconocida" %(key, value))
                    sound_chunks = 0
                    sound_pcm = b""
                    self.crear_nuevo_archivo()
            else:
                sleep((1/self.grabador.rate) * self.grabador.CHUNK)

    def crear_nuevo_archivo(self):
        print("Crear nuevo archivo?")
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
        self.archivo.setnchannels(self.channels)