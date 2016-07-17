import re
import json
import wave
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

import pyaudio

__author__ = "Daniel"

from time import sleep

import lame
from guardadores.base import GuardadorBase


class ClienteYoutube(Thread):
    def __init__(self, guardador):
        self.guardador = guardador
        self.client = socket(AF_INET, SOCK_STREAM)
        self.add = ("127.0.0.1", 9000)
        self.tabs = None
        self.tab_id = None
        super(ClienteYoutube, self).__init__()
        self.start()

    def run(self):
        print("Thread Iniciado cliente youtube")
        rep = {"\\": " ",
               "/": " ",
               ":": " ",
               "*": " ",
               "?": " ",
               '"': " ",
               "<": " ",
               ">": " ",
               "|": " "} # define desired replacements here

        # use these three lines to do the replacement
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))

        while True:
            self.client.connect(self.add)
            print("Cliente conectado")
            while True:
                #Recive la lista de tabs de youtube en formato JSON UTF-8
                print("preaparado para recivir data")
                data = self.client.recv(65536)
                self.tabs = json.loads(data.decode())
                print("Data recivida: ", data)
                print("mis tabs son: ", self.tabs)
                while self.tab_id is None:
                    #print("Esto es la tab id: ",self.tab_id)
                    sleep(0.001)
                print("Loop tab_id roto")
                self.client.send(self.tab_id.encode())
                self.tabs = None
                self.tab_id = None
                while True:
                    data = self.client.recv(65536)
                    titulo = data.decode()
                    print("Reemplazo de caracteres inadecuados INICIO")
                    titulo = pattern.sub(lambda m: rep[re.escape(m.group(0))], titulo)
                    print("Reemplazo de caracteres inadecuados FIN")
                    self.guardador.grabador.data_chunks.append({"titulo":titulo})
                    print("titulo enviado")

    def get_tabs(self):
        return self.tabs

    def set_tab(self, tab_id):
        self.tab_id = tab_id


class GuardadorWAV(GuardadorBase):
    def __init__(self, grabador):
        self.youtube = ClienteYoutube(self)
        self.PATH = "%HOMEPATH%\\grabador\\"
        super(GuardadorWAV, self).__init__(grabador)

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
                        sound = sound_pcm
                        #print(rms)
                        if rms > self.ruido_ambiente:
                            self.archivo.writeframes(sound)
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
                        elif key == "titulo":
                            self.archivo_name = self.PATH + value + ".wav"
                        else:
                            print("Data tipo %s con valor %s no reconocida" %(key, value))
                    sound_chunks = 0
                    sound_pcm = b""
                    self.crear_nuevo_archivo()
            else:
                sleep((1/self.grabador.rate) * self.grabador.CHUNK)

    def crear_nuevo_archivo(self):
        print("Crear nuevo archivo?")
        if self.archivo_name is None and self.archivo is None:
            return
        elif self.archivo_name is not None and self.archivo is not None:
            self.archivo.close()
        self.archivo_name = wave.open(self.archivo_name,"wb")

        print(self.archivo_name)

        self.archivo.setframerate(self.rate)
        self.archivo.setsampwidth(self.grabador.p.get_sample_size(self.formatM))
        self.archivo.setnchannels(self.channels)


class GuardadorMP3(GuardadorBase):
    def __init__(self, grabador):
        self.youtube = ClienteYoutube(self)
        self.PATH = "C:\\Users\\Administrador\\grabado\\"
        self.archivo_min_duration = 60
        self.grabador = grabador
        self.CHUNK = self.grabador.CHUNK
        self.formatM = pyaudio.paInt16 if 1 <= self.grabador.format_in_bits<= 16 else pyaudio.paInt32
        self.channels = self.grabador.channels
        self.rate = self.grabador.rate
        self.archivo = None
        self.archivo_name = None
        #self.crear_nuevo_archivo()
        self.tamaño_chunk_ideal = 8192
        self.ruido_ambiente = 0.00028
        self._silencio = True
        Thread.__init__(self)
        self.start()

    def run(self):
        print("GuardadorMp3 loop")
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
                            if self.archivo is None or self.archivo.closed:
                                print("Crear nuevo archivo por archivo cerrado o None")
                                self.crear_nuevo_archivo()
                            self.archivo.writeframes(sound)
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
                            print("Orden de cerrar el archivo")
                            # Crea un nuevo archivo y guarda todo lo hecho hasta ahora
                            pass
                        elif key == "titulo":
                            self.archivo_name = self.PATH + value + ".mp3"
                            print("Nuevo titulo")
                        else:
                            print("Data tipo %s con valor %s no reconocida" %(key, value))
                    sound_chunks = 0
                    sound_pcm = b""
                    if self.archivo is not None: # Nos aeguramos que el archivo no sea None
                        self.archivo.close()
                        print("Archivo cerrado")
            else:
                sleep((1/self.grabador.rate) * self.grabador.CHUNK)

    def crear_nuevo_archivo(self):
        print("Crear nuevo archivo?")
        # if self.archivo_name is None and self.archivo is None:
        #     return
        # elif self.archivo_name is not None and self.archivo is not None:
        #     self.archivo.close()
        """En teoria las lineas de arriba ya no son necesarias en ningun caso
        porque externamente cierro el archivo y como ademas, en el caso especifico
        de los grabadores youtube, la grabación no empieza hasta que haya llegado
        el nombre del archivo no existen problemas de que el nombre sea None"""

        assert self.archivo_name is not None, "Es None, no lo puedo creer ºº"
        self.archivo = lame.open(self.archivo_name,"wb")

        print(self.archivo_name)

        self.archivo.setframerate(self.rate)
        self.archivo.setsampwidth(self.grabador.p.get_sample_size(self.formatM) * 8)
        self.archivo.setnchannels(self.channels)

    def terminar(self):
        self.grabador = None
        self.youtube.client.close()