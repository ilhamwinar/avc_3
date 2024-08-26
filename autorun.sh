# !/bin/bash
# !/usr/bin/env python3

export DISPLAY=:0 #needed if you are running a simple gui app.

cd "$(dirname "$0")"

process=script_avc
while true
do

    if ! ps aux | grep -v grep | grep 'python3 avc_main2.py --id_gardu 11 --gerbang Halim' > /dev/null
    then #--nocctv 1
        python3 avc_main2.py --id_gardu 11 --gerbang Halim --rtsp_cam1 'rtsp://admin:avc12345@175.11.101.11/cam/realmonitor?channel=1&subtype=0' --rtsp_cam2 'rtsp://admin:avc12345@175.11.101.12/cam/realmonitor?channel=1&subtype=0' --rtsp_cam3 'rtsp://admin:avc12345@175.11.101.13/cam/realmonitor?channel=1&subtype=0' --rtsp_cam4 'rtsp://admin:avc12345@175.11.101.14/cam/realmonitor?channel=1&subtype=0' --rtsp_cam5 'rtsp://admin:avc12345@175.11.101.15/cam/realmonitor?channel=1&subtype=0' --endpoint_raspberry 'http://175.11.101.3:8000'  --y_trigger 350 --model_cam1 'AVC_CAM1.pt' --model_cam23 'AVC_CAM23.pt' --model_cam4 'AVC_CAM4.pt' &
        sleep 20 #--nocctv 1
    fi #--nocctv 1

sleep 10
done
exit