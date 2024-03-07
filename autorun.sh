##!/bin/bash
##!/usr/bin/env python3

export DISPLAY=:0 #needed if you are running a simple gui app.

cd "$(dirname "$0")"

process=script_avc
while true
do

    if ! ps aux | grep -v grep | grep 'python3 avc_main2.py --id_gardu 6 --gerbang CITEREUP1' > /dev/null
    then #--nocctv 1
        python3 avc_main2.py --id_gardu 6 --gerbang CITEREUP1 --rtsp_cam1 'rtsp://root:avc12345@172.20.5.146/live1s1.sdp' --rtsp_cam2 'rtsp://admin:avc12345@172.20.5.166/cam/realmonitor?channel=1&subtype=0' --rtsp_cam3 'rtsp://admin:avc12345@172.20.5.186/cam/realmonitor?channel=1&subtype=0' --rtsp_cam4 '' --endpoint_raspberry 'http://172.16.15.220:8000'  --y_trigger 455 &
        sleep 20 #--nocctv 1
    fi #--nocctv 1

    if ! ps aux | grep -v grep | grep 'python3 avc_main2.py --id_gardu 8 --gerbang CITEREUP1' > /dev/null
    then #--nocctv 1
        python3 avc_main2.py --id_gardu 8 --gerbang CITEREUP1 --rtsp_cam1 'rtsp://root:avc12345@172.20.5.148/live1s1.sdp' --rtsp_cam2 'rtsp://admin:avc12345@172.20.5.168/cam/realmonitor?channel=1&subtype=0' --rtsp_cam3 'rtsp://admin:avc12345@172.20.5.188/cam/realmonitor?channel=1&subtype=0' --rtsp_cam4 '' --endpoint_raspberry 'http://172.16.15.220:8000'  --y_trigger 455 &
        sleep 20 #--nocctv 1
    fi #--nocctv 1

    if ! ps aux | grep -v grep | grep 'python3 avc_main2.py --id_gardu 1 --gerbang CITEREUP2' > /dev/null
    then #--nocctv 1
        python3 avc_main2.py --id_gardu 1 --gerbang CITEREUP2 --rtsp_cam1 'rtsp://root:avc12345@172.20.5.141/live1s1.sdp' --rtsp_cam2 'rtsp://admin:avc12345@172.20.5.161/cam/realmonitor?channel=1&subtype=0' --rtsp_cam3 'rtsp://admin:avc12345@172.20.5.181/cam/realmonitor?channel=1&subtype=0' --rtsp_cam4 '' --endpoint_raspberry 'http://172.16.15.220:8000'  --y_trigger 450 &
        sleep 20 #--nocctv 1
    fi #--nocctv 1

    if ! ps aux | grep -v grep | grep 'python3 avc_main2.py --id_gardu 3 --gerbang CITEREUP2' > /dev/null
    then #--nocctv 1
        python3 avc_main2.py --id_gardu 3 --gerbang CITEREUP2 --rtsp_cam1 'rtsp://root:avc12345@172.20.5.143/live1s1.sdp' --rtsp_cam2 'rtsp://admin:avc12345@172.20.5.163/cam/realmonitor?channel=1&subtype=0' --rtsp_cam3 'rtsp://admin:avc12345@172.20.5.183/cam/realmonitor?channel=1&subtype=0' --rtsp_cam4 '' --endpoint_raspberry 'http://172.16.15.220:8000'  --y_trigger 455 &
        sleep 20 #--nocctv 1
    fi #--nocctv 1

sleep 10
done
exit