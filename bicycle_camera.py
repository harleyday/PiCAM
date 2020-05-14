#!/usr/bin/python3

from gpiozero import Button, PWMLED, DigitalInputDevice
from subprocess import check_call
import picamera
import io
from signal import pause
from datetime import datetime
import picamera

def shutdown():
    file = open('/mnt/camera.log','a') # make the activity LED pulse to show the camera is working
    file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tShutting down\n')
    file.close()
    activity.pulse()
    camera.stop_recording()
    camera.close() # shut down the pi if the button is held down for >2 seconds
    activity.blink(on_time=0.1, off_time=0.1, n=5, background=True)
    check_call(['sudo', 'poweroff'])
def low_battery():
    file = open('/mnt/camera.log','a') # automatically stop recording and shut down when the low battery signal is received
    file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tBattery is low\n')
    file.close()
    shutdown

# make the activity LED pulse to show the camera is working
# This script makes use of the green led which is already present in the raspberry pi zero and pi zero W
activity = PWMLED(47) # /sys/class/leds/led0
activity.pulse()

# shut down the pi if the button is held down for >2 seconds
shutdown_btn = Button(22, hold_time=2)
shutdown_btn.when_held = shutdown
print('activated shutdown button')

# automatically stop recording and shut down when the low battery signal is received
low_batt_signal = DigitalInputDevice(4, pull_up=True, bounce_time=2)
low_batt_signal.when_activated = low_battery
print('activated the low battery detection')

with picamera.PiCamera() as camera:
    start_time = datetime.now()
    camera.resolution = (1640,1232) # 1640x1232 at 30fps seems to be the resolution limit which the pi zero w gpu can handle. We could set the reolution lower to achieve higher framerates.
    camera.framerate = 30
    camera.start_recording('/mnt/' + start_time.strftime('%d-%m-%Y_%H-%M-%S') +'.h264')
    file = open('/mnt/camera.log','a')
    file.write(start_time.strftime('%d/%m/%Y, %H:%M:%S') + '\tStarting recording\n')
    file.close()
    print('now recording...')
    try:
        pause() # we wait here while the camera is recording
    except KeyboardInterrupt:
        print('Keyboard interupt')
        file = open('/mnt/camera.log','a')
        file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tKeyboard interrupt\n')
        file.close()
    except:
        print('The camera experienced an error')
        file = open('/mnt/camera.log','a')
        file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tError\n')
        file.close()
    finally:
        camera.stop_recording()
        camera.close()

print('This is the end of the script')
