#!/usr/bin/python3

from gpiozero import Button, PWMLED, DigitalInputDevice
from subprocess import check_call
import picamera
import io
from datetime import datetime

def shutdown():
    file = open('/mnt/camera.log','a') # make the activity LED pulse to show the camera is working
    file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tShutting down\n')
    file.close()
    activity.pulse()
    activity.blink(on_time=0.1, off_time=0.1, n=5, background=True)
    camera.stop_recording()
    camera.close()
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
    camera.start_recording('/mnt/' + start_time.strftime('%d-%m-%Y_%H-%M-%S') + '__1' +'.h264')
    file = open('/mnt/camera.log','a')
    file.write(start_time.strftime('%d/%m/%Y, %H:%M:%S') + '\tStarting recording\n')
    file.close()
    print('now recording...')
    try:
        i=2
        while True:
            camera.wait_recording(300) # wait here for 5 minutes while the camera records to a file
            camera.split_recording('/mnt/' + start_time.strftime('%d-%m-%Y_%H-%M-%S') + '__%d' % i +'.h264')
            i = i + 1
    except KeyboardInterrupt:
        print('Keyboard interupt')
        camera.stop_recording()
        camera.close()
        file = open('/mnt/camera.log','a')
        file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tKeyboard interrupt\n')
        file.close()
    except:
        print('The camera experienced an error')
        camera.stop_recording()
        camera.close()
        file = open('/mnt/camera.log','a')
        file.write(datetime.now().strftime('%d/%m/%Y, %H:%M:%S') + '\tError\n')
        file.close()
    finally:
        camera.stop_recording()
        camera.close()

print('This is the end of the script')
