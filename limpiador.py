import wave
from subprocess import check_output, call

__author__ = "Daniel"

import lame

directory = "C:\\Users\\Administrador\\grabado"

def get_files():
    files = check_output("dir C:\\Users\\Administrador\\grabado\\*.wav /A-d /B", shell=True).decode("cp850").strip().splitlines()
    return files

def analize_files():
    files = get_files()
    #print(files)
    for file in files:
        try:
            test = wave.open((directory + "\\" + file), "rb")
        except wave.Error:
            print("Wave raro %s" %file)
            continue
        #print(test.getduration())
        test.getnframes()/test.getframerate()
        if test.getnframes()/test.getframerate() < 60:
        #if test.getduration() < 60:
            #print(test.getduration())
            test.close()
            delete_file(file)


def delete_file(file):
    call(["del", directory + "\\" + file], shell=True)

if __name__ == "__main__":
    analize_files()