import os
import wave
from subprocess import check_output, call

import lame

__author__ = "Daniel"


directory = os.path.join(os.path.expanduser("~"), "grabado") + '\\'


def get_files():
    files = check_output("dir " + directory + "*.mp3 /A-d /B", shell=True).decode("cp850").strip().splitlines()
    return files


def analize_files():
    files = get_files()
    print("Responde s para borrar, cualquier otra cosa es no.")
    for file in files:
        try:
            test = lame.open((directory + file), "rb")
        except wave.Error:
            print("Wave raro %s" % file)
            continue
        except OSError as e:
            if e.errno == 22:
                continue
        #print(test.getduration())
        # test.getnframes()/test.getframerate()
        # if test.getnframes()/test.getframerate() < 60:
        if test.getduration() < 60:
            #print(test.getduration())
            test.close()
            if input("Borrar %s?:" % file) == "s":
                delete_file(file)


def delete_file(file):
    call(["del", directory + file], shell=True)


if __name__ == "__main__":
    analize_files()
