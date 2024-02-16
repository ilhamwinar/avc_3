import cv2
from ultralytics import YOLO
import threading
from queue import Queue
import os
from datetime import datetime
import requests
import time
import base64
import argparse
from pathlib import Path

#172.16.15.220

## ARGUMENT PARSER PARAMETER
##--------------------------------------------------------------------------------------------------##

ap = argparse.ArgumentParser()
ap.add_argument("--id_gardu",type=str, required=True,help="id_gardu")
ap.add_argument("--gerbang",type=str, required=True,help="gerbang")
ap.add_argument("--rtsp_cam1", type=str,required=True,help="insert cam1")
ap.add_argument("--rtsp_cam2", type=str, required=True,help="insert cam2")
ap.add_argument("--rtsp_cam3",type=str, required=True,help="insert cam3")
ap.add_argument("--rtsp_cam4",type=str, required=True,help="insert cam4")
#ap.add_argument("--rtsp_cam5",type=s, required=True,help="insert cam5")
ap.add_argument("--endpoint_raspberry",type=str, required=True,help="endpoint raspberry")
ap.add_argument("--y_trigger",type=int, required=True,help="y_trigger")

args = vars(ap.parse_args())

#y_trigger = 455

model = YOLO('yolov8s.pt')
model_cam1=YOLO('AVC_CAM1.pt')
model_cam23=YOLO('AVC_CAM23.pt')
model_cam4=YOLO('AVC_CAM4.pt')


# RTSP_CAM1 = 'rtsp://root:avc12345@172.20.5.143/live1s1.sdp'
# RTSP_CAM2 = 'rtsp://admin:avc12345@172.20.5.163/cam/realmonitor?channel=1&subtype=0'
# RTSP_CAM3 = 'rtsp://admin:avc12345@172.20.5.183/cam/realmonitor?channel=1&subtype=0'
# RTSP_CAM4 = 'rtsp://admin:avc12345@172.20.5.193/cam/realmonitor?channel=1&subtype=0'

# RTSP_CAM5
# MODEL_OBJECT_DETECTION_CAM12 = avc_cam12.engine
# MODEL_OBJECT_DETECTION_CAM3 = avc_cam3.engine
# RTSP_CAM1 = "rtsp://root:avc12345@10.0.25.10/live1s1.sdp"
# RTSP_CAM2 = "rtsp://admin:avc12345@10.0.25.11/cam/realmonitor?channel=1&subtype=1"
# RTSP_CAM3 = "rtsp://admin:avc12345@10.0.25.12/cam/realmonitor?channel=1&subtype=1"


# PARAMETER
RTSP_CAM1  = args["rtsp_cam1"]
RTSP_CAM2  = args["rtsp_cam2"]
RTSP_CAM3  = args["rtsp_cam3"]
RTSP_CAM4  = args["rtsp_cam4"]
#RTSP_CAM5  = args["rtsp_cam5"]

#endpoint_raspberry="http://172.20.5.132:8000"
#id_gardu="3"

endpoint_raspberry=args["endpoint_raspberry"]
id_gardu=args["id_gardu"]
gerbang=args["gerbang"]
y_trigger=args["y_trigger"]
lokasi_log=gerbang+"_"+id_gardu


## INISIALISASI CAPTURE VIDEO
cap = cv2.VideoCapture(RTSP_CAM1)
vtype=""

lastdetect = datetime.now()

def getImage2() :
    global f2
    cap = cv2.VideoCapture(RTSP_CAM2)
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            f2 = frame.copy()

def getImage3() :
    global f3
    cap = cv2.VideoCapture(RTSP_CAM3)
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            f3 = frame.copy()

def getImage4() :
    global f4
    cap = cv2.VideoCapture(RTSP_CAM4)
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            f4 = frame.copy()

def present_avc(id_gardu,vtype_koreksi,time_detect,img_path,endpoint_raspberry):
    try :
        url_ping = endpoint_raspberry+"/avc/ping"  # Replace with the actual API URL
        
        
        # Send a GET request to the URL
        response = requests.get(url_ping)

        # Check if the request was successful (status code 200)
        try:
            api_present = endpoint_raspberry+"/avc/present/"
            if response.status_code == 200:
                # Parse the JSON data from the response
                data = response.json()
                print(data)
                
                tmpid_gardu="?idgardu="+str(id_gardu)
                tmpgolongan="&golongan="+str(vtype_koreksi)
                tmpwaktu="&waktu="+str(time_detect)
                tmpimgpath="&imgpath="+str(img_path)
                
                TMPAPI_ENDPOINT=api_present+tmpid_gardu+tmpgolongan+tmpwaktu+tmpimgpath
                
                # sending post request and saving response as response object
                r = requests.post(url=TMPAPI_ENDPOINT)
                print(r.json())

            else:
                print(f"Request failed with status code: {response.status_code}")
        except:
            print(f"Request failed with status code: {500}")
            pass
    except:
        print(f"cannot ping to raspberry")
        pass



def send_image(base64_data,golongan,golongan_koreksi,waktu,tipe_cam,endpoint_raspberry):
    # Replace the URL with the actual API endpoint
    api_url = endpoint_raspberry+"/avc/upload_image/"

    # JSON data to be sent in the POST request
    json_data = {
    "base64_data": base64_data,
    "golongan": golongan,
    "golongan_koreksi": golongan_koreksi,
    "waktu": waktu,
    "tipe_cam": tipe_cam
    }

    # Set the headers to indicate that you're sending JSON data
    headers = {
        "Content-Type": "application/json",
    }

    try:
        # Make the POST request
        response = requests.post(api_url, json=json_data, headers=headers)

        # Check if the request was successful (status code 2xx)
        if response.status_code // 100 == 2:
            print("POST request successful to send Image!")
            print("Response:", response.json())
        else:
            print(f"Error: {response.status_code}\n{response.text}")

    except Exception as e:
        print(f"Error: {e}")

def update_to_db(path,golongan,golongan_koreksi,waktu,endpoint_raspberry):
    # Replace the URL with the actual API endpoint
    api_url = endpoint_raspberry+"/avc/update_img_to_db/"

    # JSON data to be sent in the POST request
    json_data = {
    "path_image": path,
    "golongan":golongan,
    "golongan_koreksi":golongan_koreksi,
    "waktu": waktu
    }

    # Set the headers to indicate that you're sending JSON data
    headers = {
        "Content-Type": "application/json",
    }

    try:
        # Make the POST request
        response = requests.post(api_url, json=json_data, headers=headers)

        # Check if the request was successful (status code 2xx)
        if response.status_code // 100 == 2:
            print("POST request successful!")
            print("Response:", response.json())
        else:
            print(f"Error: {response.status_code}\n{response.text}")

    except Exception as e:
        print(f"Error: {e}")

## FUNGSI UNTUK READ LOG
def write_log(lokasi_log, datalog):
    waktulog = datetime.now()
    dirpathlog = f"Log/{lokasi_log}"
    os.makedirs(dirpathlog, exist_ok=True)
    pathlog = f"{waktulog.strftime('%d%m%Y')}.log"
    file_path = Path(f"{dirpathlog}/{pathlog}")
    datalog = "[INFO] - " + datalog
    if not file_path.is_file():
        file_path.write_text(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
    else :
        fb = open(f"{dirpathlog}/{pathlog}", "a")
        fb.write(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
        fb.close
    
    print(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}")

def write_log_error(lokasi_log, datalog):
    waktulog = datetime.now()
    dirpathlog = f"Log/{lokasi_log}"
    os.makedirs(dirpathlog, exist_ok=True)
    pathlog = f"{waktulog.strftime('%d%m%Y')}.log"
    file_path = Path(f"{dirpathlog}/{pathlog}")
    datalog = "[ERROR] - " + datalog
    if not file_path.is_file():
        file_path.write_text(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
    else :
        fb = open(f"{dirpathlog}/{pathlog}", "a")
        fb.write(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
        fb.close
    
    print(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}")

## STARTUP THREADHING
try:
    p2 = threading.Thread(target=getImage2)
    p3 = threading.Thread(target=getImage3)
    p4 = threading.Thread(target=getImage4)

    p2.start()
    p3.start()
    p4.start()
except:
    pass

time.sleep(3)


while cap.isOpened():
    success, frame = cap.read()
    if success:
        waktu = datetime.now()
        f1 = frame.copy()

        #Citereup
        cv2.rectangle(frame, (0,0), (200, 720), (0,0,0), -1)
        cv2.rectangle(frame, (0,500), (1280, 720), (0,0,0), -1)
        
        #Tracking AI
        results = model.track(frame, persist=True, conf=0.4 , classes=[2,5,7], verbose=False, agnostic_nms=False, max_det=1)

        try:
            for i, r in enumerate(results):
                for index, box in enumerate(r.boxes):
                        tracker_id = box.id
        except:
            print("no detection")
            pass

        frame = results[0].plot(line_width=1, labels=True, conf=True)

        #CITEREUP 2_3
        cv2.line(frame, (600,y_trigger), (1100,y_trigger), (255,255,255), 3)

        result2=[]

        if len(results[0].boxes.cls) > 0 :
            #id_box=results[0].boxes.data.tolist()[0][4]
            
            for i in results[0].boxes :
                xyxy = i.xyxy

                #DETECTION FOR TRIGER
                if i.xyxy[0][3] >= y_trigger - 5 and i.xyxy[0][3] < y_trigger + 20 and abs(waktu - lastdetect).seconds > 2 :
                    write_log(lokasi_log,"Triggered by AI VRTUAL LINE")
                    lastdetect = datetime.now()
                    try:
                        print("")

                        ## SHOW IMAGE CAPTURE 
                        cv2.imshow('CAM 1 '+lokasi_log, f1)
                        cv2.imshow('CAM 2 '+lokasi_log, f2)
                        cv2.imshow('CAM 3 '+lokasi_log, f3)

                        ## Save as base64 

                        b64_bytes_cam1 = cv2.imencode('.jpg', f1)
                        base64_data_cam1 = base64.b64encode(b64_bytes_cam1[1]).decode('utf-8')

                        b64_bytes_cam2 = cv2.imencode('.jpg', f2)
                        base64_data_cam2 = base64.b64encode(b64_bytes_cam2[1]).decode('utf-8')

                        b64_bytes_cam3 = cv2.imencode('.jpg', f3)
                        base64_data_cam3 = base64.b64encode(b64_bytes_cam3[1]).decode('utf-8')

                        if RTSP_CAM4 != '':
                            cv2.imshow('CAM 4 '+lokasi_log, f4)
                            b64_bytes_cam4 = cv2.imencode('.jpg', f4)
                            base64_data_cam4 = base64.b64encode(b64_bytes_cam4[1]).decode('utf-8')

                        write_log(lokasi_log,"SAVE ALL IMAGE SUCCESSED BASE64")

                    except:
                        write_log_error(lokasi_log,"SAVE ALL IMAGE SUCCESSED BASE64")
                        pass


                    time_object = datetime.now()
                    time_image = time_object.strftime("%d%m%y-%H%M%S")
                    time_detect = time_object.strftime("%Y-%m-%d %H:%M:%S")


                    # Thread Image Detection
                    # ====================================
                    # Model Categories Cam 1 and Cam 2
                    # 0 = Bus
                    # 1 = Car
                    # 2 = One Tire
                    # 3 = Two Tire
                    # 4 = Truck Large
                    # 5 = Truck Small
                    # ====================================
                    # Model Categories Cam 3
                    # 0 = single tire
                    # 1 = One Tire
                    # 2 = Three Tire
                    # 3 = Two Tire
                    # ====================================
                    # Model Categories Cam 4
                    # 0 = Double Ban
                    # 1 = Double Tire
                    # 2 = Single Tire
                    # 3 = Tertutup

                    vtype=""
                    vtype_koreksi=""
                    result_cam1=model_cam1.predict(f1, conf=0.4,verbose=False)
                    for r in result_cam1:
                        write_log(lokasi_log,"LIST DARI RESULT CAM1: "+str(r.boxes.cls.tolist()))
                        #print("LIST DARI RESULT CAM1: "+str(r.boxes.cls.tolist()))
                        temp_golongan1= r.boxes.cls.tolist()
                            
                    temp_golongan1.sort()
                    # Filter Remove One Tire, Two Tire,and Three Tire Detection
                    result1 = [x for x in temp_golongan1 if x != 2 and x != 3]
                    write_log(lokasi_log,"LIST SORT RESULT CAM1 AND CAM2: "+str(result1))

                    try:
                        if int(result1[0]) == 0:
                            # Golongan 1 Bus
                            vtype = 1
                            vtype_koreksi=1
                            write_log(lokasi_log,"GOL 1 BIS DETECTED")
                            
                        elif int(result1[0]) == 1:
                            # Golongan 1
                            vtype = 0
                            vtype_koreksi=0
                            write_log(lokasi_log,"GOL 1 MOBIL DETECTED")

                        else:
                            try:
                                result_cam2=model_cam1.predict(f2, conf=0.4,verbose=False)
                                for r in result_cam2:
                                    write_log(lokasi_log,"LIST DARI RESULT CAM2: "+str(r.boxes.cls.tolist()))
                                    #print("LIST DARI RESULT CAM 2: "+str(r.boxes.cls.tolist()))
                                    temp_golongan2= r.boxes.cls.tolist()
                                    
                                temp_golongan2.sort()
                                result2 = [x for x in temp_golongan2 if x !=0 and x != 1 and x != 4 and x != 5]
                                write_log(lokasi_log,"LIST SORT RESULT CAM2 dan CAM3: "+str(result2))
                               
                            except:
                                write_log_error(lokasi_log,"TIDAK ADA PREDIKSI DARI CAM 2")
                                pass
                            # Truck L and Double Two Tire
                            try:
                                if (result1[0] == 4 and result2[0] == 3 and result2[1] == 3):
                                    # Golongan 5
                                    vtype = 5
                                    vtype_koreksi=5
                                    write_log(lokasi_log,"GOL 5 DETECTED")
                                    #print("GOL5")

                                    # Truck L and Double One Tire
                                elif (result1[0] == 4 and result2[0] == 2 and result2[1] == 2):
                                    # Check Cam 3
                                    result_cam3=model_cam23.predict(f3, conf=0.4,verbose=False)
                                    for r in result_cam3:
                                        temp_golongan3= r.boxes.cls.tolist()
                                        
                                    temp_golongan3.sort()
                                    result3 = [x for x in temp_golongan3 if x !=0 and x != 1 and x != 4 and x != 5]
                                    write_log(lokasi_log,"LIST SORT RESULT CAM3: "+str(result3))
                                    #print(result3)
                                    if 2 in result3:
                                        vtype = 5
                                        vtype_koreksi=5
                                        #print("GOL 5 VIA CAM 3")
                                        write_log(lokasi_log,"GOL 5 DETECTED VIA CAM3")
                                    else:
                                        vtype = 4
                                        vtype_koreksi=4
                                        write_log(lokasi_log,"GOL 4 DETECTED")


                                elif (result1[0] == 4 and result2[0] == 2 and result2[1] == 3):
                                    
                                    result_cam3=model_cam23.predict(f3, conf=0.4,verbose=False)
                                    for r in result_cam3:
                                        #print("LIST DARI RESULT 3: "+str(r.boxes.cls.tolist()))
                                        write_log(lokasi_log,"LIST PREDICT RESULT CAM3: "+str(r.boxes.cls.tolist()))
                                        temp_golongan3= r.boxes.cls.tolist()
                                    
                                    temp_golongan3.sort()
                                    result3 = [x for x in temp_golongan3 if x !=0 and x != 1 and x != 4 and x != 5]
                                    write_log(lokasi_log,"LIST SORT RESULT CAM3: "+str(result3))
                                    
                                    if 3 in result3:
                                        vtype = 4
                                        vtype_koreksi=4
                                        write_log(lokasi_log,"GOL 4 DETECTED VIA CAM3")
                                    else:
                                        vtype = 5
                                        vtype_koreksi=5
                                        write_log(lokasi_log,"GOL 5")
                                        #print("GOL 5")
                            except:
                                write_log_error(lokasi_log,"bukan golongan 4 atau 5")

                                pass

                    # Truck L and Two Tire
                            if ((result1[0] == 4 and result2[0] == 3) and (vtype != 4 and vtype != 5)):
                            # Golongan 3, coba tambahkan one tire, one tire untuk kasus golongan 3 yang heran. untuk golongan 4 gandeng, prioritas cam 3 deteksi sorting one tire, one tire.
                                    vtype = 3
                                    vtype_koreksi=3
                                    write_log(lokasi_log,"GOL 3 DETECTED")
                                    #print("GOL 3")

                            elif ((result1[0] == 4 and result2[0] == 2) and (vtype != 4 and vtype != 5)):
                                # Golongan 3, coba tambahkan one tire, one tire untuk kasus golongan 3 yang heran. untuk golongan 4 gandeng, prioritas cam 3 deteksi sorting one tire, one tire.
                                vtype = 2
                                
                                #print("GOL 2")
                                write_log(lokasi_log,"GOL 2 START DETECTED")

                                if RTSP_CAM4 !='':
                                    result_cam4=model_cam4.predict(f4, conf=0.3,verbose=False)

                                    for r in result_cam4:
                                        #print("LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                                        write_log(lokasi_log,"LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                                        temp_golongan4= r.boxes.cls.tolist()

                                    ## PLOTING FOR CAM4
                                    f4= result_cam4[0].plot(line_width=1, labels=True, conf=True)
                                    cv2.imshow('CAM deteksi cam4', f4)
                                    
                                    #KOREKSI AI JADI GOL 1
                                    print(str(temp_golongan4))
                                    if 1 in temp_golongan4: 
                                        vtype = 2
                                        vtype_koreksi = 2
                                        write_log(lokasi_log,"GOL 2 END DETECTED")
                                        #print("GOL 2")
                                    elif 0 in temp_golongan4: 
                                        vtype = 2
                                        vtype_koreksi = 2
                                        write_log(lokasi_log,"GOL 2 END DETECTED")
                                        #print("GOL 2")
                                    elif 2 in temp_golongan4:
                                        # Golongan 0
                                        vtype = 0
                                        vtype_koreksi = 0
                                        #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK")
                                        write_log(lokasi_log,"GOL 2 CHANGE TO GOL 1 TRUCK DETECTED")
                                    elif not temp_golongan4:
                                        vtype = 0
                                        vtype_koreksi = 0
                                        #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK")
                                        write_log(lokasi_log,"GOL 2 CHANGE TO GOL 1 TRUCK DETECTED")
                                    write_log(lokasi_log,"GOL 2 BERUBAH MENJADI: " + str(vtype))
                                    #print("GOL 2 BERUBAH MENJADI: " + str(vtype))
                                else:
                                    vtype = 2

                                
                        # Truck L or Truck S
                            elif ((result1[0] == 5 or result1[0] == 4) and (vtype != 4 and vtype != 5)):
                                # tanpa cam4
                                #print("KESINI 5 ATAU 4, LOGIC GOL 2")
                                vtype=2
                                write_log(lokasi_log,"GOL 2 START DETECTED")

                                if RTSP_CAM4 !='':
                                    result_cam4=model_cam4.predict(f4, conf=0.3,verbose=False)

                                    ## PLOTING FOR CAM4
                                    f4= result_cam4[0].plot(line_width=1, labels=True, conf=True)
                                    cv2.imshow('CAM deteksi cam4', f4)


                                    for r in result_cam4:
                                        #print("LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                                        write_log(lokasi_log,"LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                                        temp_golongan4= r.boxes.cls.tolist()
                                    
                                    #KOREKSI AI JADI GOL 1
                                    print(str(temp_golongan4))
                                    if 1 in temp_golongan4: 
                                        vtype=2
                                        vtype_koreksi=2
                                        #print("GOL 2")
                                        write_log(lokasi_log,"GOL 2 START DETECTED")
                                    elif 0 in temp_golongan4: 
                                        vtype=2
                                        vtype_koreksi=2
                                        #print("GOL 2")
                                        write_log(lokasi_log,"GOL 2 START DETECTED")
                                    elif 2 in temp_golongan4:
                                        # Golongan 0
                                        vtype=0
                                        vtype_koreksi=0
                                        #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK SINGLE TIRE")
                                        write_log(lokasi_log,"GOL 2 CHANGE TO GOL 1 TRUCK SINGLE TIRE DETECTED")

                                    elif not temp_golongan4:
                                        vtype=0
                                        vtype_koreksi=0
                                        write_log(lokasi_log,"GOL 2 CHANGE TO GOL 1 TRUCK SINGLE TIRE DETECTED")
                                        #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK TIDAK TERDETEKSI")
                                    write_log(lokasi_log,"GOL 2 BERUBAH MENJADI: " + str(vtype))
                                else:
                                    vtype=2

                    except:
                        write_log_error(lokasi_log,"NOT GETTING VEHICLE GOLONGAN")
                        continue

                            ## Golongan 2 dengan cam 4
                        
                    #     result_cam4=model_cam4.predict(f4, conf=0.4,verbose=False)
                    #     for r in result_cam4:
                    #         print("LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                    #         temp_golongan4= r.boxes.cls.tolist()
                        
                    #     #KOREKSI AI JADI GOL 1
                    #     print(str(temp_golongan4))
                    #     if 1 in temp_golongan4: 
                    #         vtype = 2
                    #         print("GOL 2")
                    #     elif 0 in temp_golongan4: 
                    #         vtype = 2
                    #         print("GOL 2")
                    #     elif 2 in temp_golongan4:
                    #         # Golongan 0
                    #         vtype = 1
                    #         print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK")
                    #     elif not temp_golongan4:
                    #         vtype = 1
                    #         print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK")
                    # print("GOL 2 BERUBAH MENJADI: " + str(vtype))

                    #


                    # img1 = (
                    #     datapath
                    #     + "/"
                    #     + str(vtype_koreksi)
                    #     + "/"
                    #     + time_image
                    #     + "-"
                    #     + str(vtype)
                    #     + "-"
                    #     + str(vtype_koreksi)
                    #     + "-"
                    #     + "cam1.jpg"
                    # )
                    # img2 = (
                    #     datapath
                    #     + "/"
                    #     + str(vtype_koreksi)
                    #     + "/"
                    #     + time_image
                    #     + "-"
                    #     + str(vtype)
                    #     + "-"
                    #     + str(vtype_koreksi)
                    #     + "-"
                    #     + "cam2.jpg"
                    # )
                    # img3 = (
                    #     datapath
                    #     + "/"
                    #     + str(vtype_koreksi)
                    #     + "/"
                    #     + time_image
                    #     + "-"
                    #     + str(vtype)
                    #     + "-"
                    #     + str(vtype_koreksi)
                    #     + "-"
                    #     + "cam3.jpg"
                    # )

                    # img4 = (
                    #     datapath
                    #     + "/"
                    #     + str(vtype)
                    #     + "/"
                    #     + time_image
                    #     + "-"
                    #     + str(vtype)
                    #     + "-"
                    #     + str(vtype_koreksi)
                    #     + "-"
                    #     + "cam4.jpg"
                    # )

                    # cv2.imwrite(img1, f1)
                    # cv2.imwrite(img2, f2)
                    # cv2.imwrite(img3, f3)
                    # cv2.imwrite(img4, f4)

                    img_path=time_image+ "-"+ str(vtype)+ "-"+ str(vtype_koreksi)
                    print(img_path)

                    try :
                        url_ping = endpoint_raspberry+"/avc/ping"  # Replace with the actual API URL
                        
                        # Send a GET request to the URL
                        response = requests.get(url_ping)

                        # Check if the request was successful (status code 200)
                        try:
                            if response.status_code == 200:

                                ## present new
                                present_avc(id_gardu,vtype_koreksi,time_detect,img_path,endpoint_raspberry)

                                ## Send image api
                                try:
                                    send_image(base64_data_cam1,str(vtype),str(vtype_koreksi),time_image,"1",endpoint_raspberry)
                                    send_image(base64_data_cam2,str(vtype),str(vtype_koreksi),time_image,"2",endpoint_raspberry)
                                    send_image(base64_data_cam3,str(vtype),str(vtype_koreksi),time_image,"3",endpoint_raspberry)
                                    if RTSP_CAM4 !="":
                                        send_image(base64_data_cam4,str(vtype),str(vtype_koreksi),time_image,"4",endpoint_raspberry)
                                    
                                except:
                                    write_log_error(lokasi_log,f"ERROR KIRIM GAMBAR")
                                    #print(f"ERROR KIRIM GAMBAR")

                                ## update to db
                                try:
                                    update_to_db(img_path,str(vtype),str(vtype_koreksi),time_detect,endpoint_raspberry)
                                    #print(f"BERHASIL UPDATE DB")
                                    write_log(lokasi_log,f"BERHASIL UPDATE DB")
                                except:
                                    write_log_error(lokasi_log,f"ERROR UPDATE DB")
                                    #print(f"ERROR UPDATE DB")
                            else:
                                #print(f"Request failed with status code: {response.status_code}")
                                write_log_error(lokasi_log,f"Request failed with status code: {response.status_code}")

                        except:
                            pass
                    except:
                        #print(f"cannot ping to raspberry")
                        write_log_error(lokasi_log,f"cannot ping to raspberry")
                        continue
        #print to imshow
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,500)
        fontScale              = 1
        fontColor              = (255,255,255)
        thickness              = 3
        lineType               = 2

        if vtype!="":
            vtype_print=vtype
        try:
            cv2.putText(frame,'golongan: '+str(vtype_print), 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)

        except:
            pass

        vtype=""
        cv2.imshow('CAM LIVE', frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
