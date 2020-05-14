#!/bin/bash

install_apt_packages(){
    echo "::: Installing required apt packages and dependencies"
    apt-get install python3 python3-gpiozero python3-picamera python3-pip
}

update_scripts(){
    echo "::: Fetching updates from GitHub"
    git pull
}

install_python_packages(){
    echo "::: Installing required python3 packages"
    python3 -m pip install datetime
}

install_service(){
    echo "::: Installing the systemd service file and enabling it"
    cp bicycle_camera.service /etc/systemd/system
    systemctl daemon-reload
    systemctl enable bicycle_camera.service
    systemctl start bicycle_camera.service
    echo "::: The bicycle camera is running, and will start automatically every time you start the machine"
    echo "::: To turn off the camera, hold down the button for 3 seconds, then wait for the green light to turn off, then slide the switch into the off position."
}

remove_scripts(){
    echo "::: Removing the PiCAM software and dependencies"
    systemctl stop bicycle_camera.service
    systemctl daemon-reload
    systemctl disable bicycle_camera.service
    rm /etc/systemd/system/bicycle_camera.service
    apt-get autoremove python3-gpiozero python3-picamera
    python3 -m pip uninstall datetime
}

scriptusage(){
    echo "::: Installs PiCAM scripts"
    echo ":::"
    echo "::: Usage: pivpn <-up|update> [-h|help]"
    echo ":::"
    echo "::: Commands:"
    echo ":::  [none]              Installs PiCAM from master branch"
    echo ":::  -up, update         Updates from test branch"
    echo ":::  -h, help            Show this usage dialog"
}

## script

if [[ $# -eq 0 ]]; then
    install_apt_packages
    install_python_packages
    install_service
else
  while true; do
    case "$1" in
      -up|update)
          update_scripts
          exit 0
          ;;
      -rm|remove)
          remove_scripts
          exit 0
          ;;
      -h|help)
          scriptusage
          exit 0
          ;;
      *)
        install_apt_packages
        install_python_packages
        install_service
        exit 0
        ;;
    esac
  done
fi
