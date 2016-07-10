import comtypes
from pycaw.pycaw import AudioUtilities, CLSID_MMDeviceEnumerator, IMMDeviceEnumerator

__author__ = "Daniel"

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
for device in AudioUtilities.GetAllDevices():
    print(device)
    if device.FriendlyName == "Altavoz/Auricular (Realtek High Definition Audio)":
    #if device.FriendlyName == "CABLE Input (VB-Audio Virtual Cable)":
        print("HOLAAAAAAAA")
        deviceEnumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator,
            IMMDeviceEnumerator,
            comtypes.CLSCTX_INPROC_SERVER)
        speakers = deviceEnumerator.GetDevice(
                    device.id)
        devices = speakers
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
print(volume.GetMute())
print(volume.GetMasterVolumeLevel())
print(volume.GetVolumeRange())
#volume.SetMasterVolumeLevel(-20.0, None)
volume.VolumeStepDown(None)
print(volume.GetMasterVolumeLevel())
#volume.caca()