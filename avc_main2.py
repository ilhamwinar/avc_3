import cv2
from ultralytics import YOLO
import threading
from queue import Queue
import os
from datetime import datetime
import requests
import time
import base64
from pathlib import Path
import argparse

#argumentparser
ap = argparse.ArgumentParser()
ap.add_argument("--id_gardu",type=str, required=True,help="id_gardu")
ap.add_argument("--gerbang",type=str, required=True,help="gerbang")
ap.add_argument("--rtsp_cam1", type=str,required=True,help="insert cam1")
ap.add_argument("--rtsp_cam2", type=str, required=True,help="insert cam2")
ap.add_argument("--rtsp_cam3",type=str, required=True,help="insert cam3")
ap.add_argument("--rtsp_cam4",type=str, required=True,help="insert cam4")
ap.add_argument("--rtsp_cam5",type=str, required=True,help="insert cam5")
ap.add_argument("--endpoint_raspberry",type=str, required=True,help="endpoint raspberry")
ap.add_argument("--y_trigger",type=int, required=True,help="y_trigger")
ap.add_argument("--model_cam1",type=str, required=True,help="model_cam1")
ap.add_argument("--model_cam23",type=str, required=True,help="model_cam23")
ap.add_argument("--model_cam4",type=str, required=True,help="model_cam4")

args = vars(ap.parse_args())

#Parameter

# PARAMETER
RTSP_CAM1  = args["rtsp_cam1"]
#RTSP_CAM1 = 'rtsp://root:avc12345@172.20.5.143/live1s1.sdp'
RTSP_CAM2  = args["rtsp_cam2"]
#RTSP_CAM2 = 'rtsp://admin:avc12345@172.20.5.163/cam/realmonitor?channel=1&subtype=0'
RTSP_CAM3  = args["rtsp_cam3"]
#RTSP_CAM3 = 'rtsp://admin:avc12345@172.20.5.183/cam/realmonitor?channel=1&subtype=0'
RTSP_CAM4  = args["rtsp_cam4"]
#RTSP_CAM4 = 'rtsp://admin:avc12345@172.20.5.213/cam/realmonitor?channel=1&subtype=0'
RTSP_CAM5  = args["rtsp_cam5"]
#RTSP_CAM5 = 'rtsp://admin:avc12345@172.20.5.193/cam/realmonitor?channel=1&subtype=0'


endpoint_raspberry=args["endpoint_raspberry"]
#endpoint_raspberry="http://172.20.5.132:8000"
id_gardu=args["id_gardu"]
#id_gardu="3"
gerbang=args["gerbang"]
y_trigger=args["y_trigger"]
model_cam1=args["model_cam1"]
model_cam23=args["model_cam23"]
model_cam4=args["model_cam4"]
lokasi_log=gerbang+"_"+id_gardu

model = YOLO('yolov8s.pt')
model_cam1=YOLO(model_cam1)
model_cam23=YOLO(model_cam23)
model_cam4=YOLO(model_cam4)

directory = os.getcwd()
datapath=directory+"/img"
API_ENDPOINT = endpoint_raspberry+"/avc/present/"

def getImage2() :
    global f2
    global statcam2

    cap = cv2.VideoCapture(RTSP_CAM2)
    while cap.isOpened():
        success, frame = cap.read()
        global stopthread
        if stopthread == True :
            break

        if success:
            statcam2 = True
            f2 = frame.copy()
        else :
            statcam2 = False
            write_log_error(lokasi_log,"CAM 2 OFF")
            break

def getImage3() :
    global f3
    global statcam3
    cap = cv2.VideoCapture(RTSP_CAM3)
    while cap.isOpened():
        success, frame = cap.read()
        global stopthread
        if stopthread == True :
            break
        if success:
            statcam3 = True
            f3 = frame.copy()
        else :
            statcam3 = False
            write_log_error(lokasi_log,"CAM 3 OFF")
            break

def getImage4() :
    global f4
    global statcam4
    cap = cv2.VideoCapture(RTSP_CAM4)
    while cap.isOpened():
        success, frame = cap.read()
        global stopthread
        if stopthread == True :
            break
        if success:
            statcam4 = True
            f4 = frame.copy()
        else :
            statcam4 = False
            write_log_error(lokasi_log,"CAM 4 OFF")
            break

def getImage5() :
    global f5
    global statcam5
    cap = cv2.VideoCapture(RTSP_CAM5)
    while cap.isOpened():
        success, frame = cap.read()
        global stopthread
        if stopthread == True :
            break
        if success:
            statcam5 = True
            f5 = frame.copy()
        else :
            statcam5 = False
            write_log_error(lokasi_log,"CAM 5 OFF")
            break


## FUNGSI UNTUK READ LOG
def write_log(lokasi_write_log, datalog):
    waktulog = datetime.now()
    dirpathlog = f"Log/{lokasi_write_log}"
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

def write_log_error(lokasi_write_log, datalog):
    waktulog = datetime.now()
    dirpathlog = f"Log/{lokasi_write_log}"
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

def write_status_active(file_name):
    # Get the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Format the status report
    report = f"{current_time}"
    # Write the status report to a text file
    try:
        with open(file_name, "w") as file:
            file.write(report)
            write_log(lokasi_log,"BERHASIL WRITE FILE MULAI WAKTU AVC AKTIF")
    except:
        write_log(lokasi_log_error,"GAGAL WRITE FILE MULAI WAKTU AVC AKTIF")
        pass

def present_avc(id_gardu,vtype_koreksi,time_detect,img_path,endpoint_raspberry):
    try :
        url_ping = endpoint_raspberry+"/avc/ping"  # Replace with the actual API URL

        # Check if the request was successful (status code 200)
        try:
            api_present = endpoint_raspberry+"/avc/present/"
            if response.status_code == 200:
                # Parse the JSON data from the response
                data = response.json()
                
                tmpid_gardu="?idgardu="+str(id_gardu)
                tmpgolongan="&golongan="+str(vtype_koreksi)
                tmpwaktu="&waktu="+str(time_detect)
                tmpimgpath="&imgpath="+str(img_path)
                
                TMPAPI_ENDPOINT=api_present+tmpid_gardu+tmpgolongan+tmpwaktu+tmpimgpath
                
                # sending post request and saving response as response object
                r = requests.post(url=TMPAPI_ENDPOINT)

            else:
                write_log_error(lokasi_log,f"Request failed with status code: {response.status_code}")
        except:
            write_log_error(lokasi_log,f"Request failed with status code: {500}")
            pass
    except:
        write_log_error(lokasi_log,f"cannot ping to raspberry")
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
            write_log(lokasi_log,"POST request successful to send Image!")
        else:
            write_log_error(lokasi_log,f"Error: {response.status_code}\n{response.text}")

    except Exception as e:
        write_log_error(lokasi_log,f"Error: {e}")
        

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
            write_log(lokasi_log,"POST request UPDATE DB SUCCESSED!")
            #write_log(lokasi_log,"Response:", response.json())
        else:
            write_log_error(lokasi_log,f"Error: {response.status_code}\n{response.text}")

    except Exception as e:
        write_log_error(lokasi_log,f"Error: {e}")

stopthread = False

p2 = threading.Thread(target=getImage2)
p3 = threading.Thread(target=getImage3)
p4 = threading.Thread(target=getImage4)
p5 = threading.Thread(target=getImage5)

p2.start()
p3.start()
p4.start()
p5.start()

time.sleep(10)

cap = cv2.VideoCapture(RTSP_CAM1)

#CITEREUP 2_3
# y_trigger = 420

#CIKATAMA
# y_trigger = 530

temp_id=0
vtype=""
lastdetect = datetime.now()
write_log(lokasi_log,"PROGRAM AVC MINI PC STARTED")
write_status_active(lokasi_log+".txt")

while cap.isOpened():
    success, frame = cap.read()
    if success:
    

        if statcam2 == False or statcam3 == False or statcam4 == False or statcam5 == False :
            stopthread = True
            time.sleep(3)
            write_log(lokasi_log,f"CAM 2 {p2.is_alive()}")
            write_log(lokasi_log,f"CAM 3 {p3.is_alive()}")
            write_log(lokasi_log,f"CAM 4 {p4.is_alive()}")
            write_log(lokasi_log,f"CAM 5 {p5.is_alive()}")
            write_log_error(lokasi_log,"FORCE EXIT BECAUSE ONE OF CAMERA LOST CONNECTION OR CRASHED")
            exit()
        waktu = datetime.now()
        f1 = frame.copy()

        #Citereup
        cv2.rectangle(frame, (0,0), (200, 720), (0,0,0), -1)
        cv2.rectangle(frame, (0,500), (1280, 720), (0,0,0), -1)
        
        #Tracking AI
        results = model.track(frame, persist=True, conf=0.4 , classes=[2,5,7], verbose=False, agnostic_nms=False, max_det=2)

        try:
            for i, r in enumerate(results):
                for index, box in enumerate(r.boxes):
                        tracker_id = box.id
        except:
            pass

        frame = results[0].plot(line_width=1, labels=True, conf=True)

        #CITEREUP 2_3
        cv2.line(frame, (600,y_trigger), (1100,y_trigger), (255,255,255), 3)

        result2=[]

        if len(results[0].boxes.cls) > 0 :
            #id_box=results[0].boxes.data.tolist()[0][4]
            
            for i in results[0].boxes :
                xyxy = i.xyxy
                #if temp_id != id_box:
                
                #DETECTION FOR TRIGER
                if i.xyxy[0][3] >= y_trigger - 5 and i.xyxy[0][3] < y_trigger + 20 and abs(waktu - lastdetect).seconds > 2 :
                    #print("TEST TRIGGERED")
                    write_log(lokasi_log,"TRIGGERED GAMBAR")
                    lastdetect = datetime.now()
                    try:
                        ## SHOW IMAGE CAPTURE 
                        # cv2.imshow('CAM 1 '+id_gardu, f1)
                        # cv2.imshow('CAM 2 '+id_gardu, f2)
                        # cv2.imshow('CAM 3 '+id_gardu, f3)
                        # cv2.imshow('CAM 4 '+id_gardu, f4)
                        # cv2.imshow('CAM 5 '+id_gardu, f5)


                        ## Save as base64 
                        cv2.imwrite("CAM1.jpg", f1)
                        cv2.imwrite("CAM2.jpg", f2)
                        cv2.imwrite("CAM3.jpg", f3)
                        cv2.imwrite("CAM4.jpg", f4)
                        cv2.imwrite("CAM5.jpg", f5)

                        b64_bytes_cam1 = cv2.imencode('.jpg', f1)
                        base64_data_cam1 = base64.b64encode(b64_bytes_cam1[1]).decode('utf-8')
                        write_log(lokasi_log,"CONVERT CAM1 TO BASE 64")

                        b64_bytes_cam2 = cv2.imencode('.jpg', f2)
                        base64_data_cam2 = base64.b64encode(b64_bytes_cam2[1]).decode('utf-8')
                        write_log(lokasi_log,"CONVERT CAM2 TO BASE 64")

                        b64_bytes_cam3 = cv2.imencode('.jpg', f3)
                        base64_data_cam3 = base64.b64encode(b64_bytes_cam3[1]).decode('utf-8')
                        write_log(lokasi_log,"CONVERT CAM3 TO BASE 64")


                        b64_bytes_cam4 = cv2.imencode('.jpg', f4)
                        base64_data_cam4 = base64.b64encode(b64_bytes_cam4[1]).decode('utf-8')
                        write_log(lokasi_log,"CONVERT CAM4 TO BASE 64")


                    except:
                        write_log_error(lokasi_log,"GAGAL CONVERT CAM TO BASE 64")
                        pass

                    time_object = datetime.now()
                    time_image = time_object.strftime("%d%m%y-%H%M%S")
                    time_detect = time_object.strftime("%Y-%m-%d %H:%M:%S")

 
                    #without CAM4
                    #cv2.imshow('CAM 4', f4)

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
                    write_log(lokasi_log,"CAM1 STARTED TO PREDICT")
                    for r in result_cam1:
                        #print("LIST DARI RESULT CAM1: "+str(r.boxes.cls.tolist()))
                        temp_golongan1= r.boxes.cls.tolist()
                            
                    temp_golongan1.sort()
                    # Filter Remove One Tire, Two Tire,and Three Tire Detection
                    result1 = [x for x in temp_golongan1 if x != 2 and x != 3]
                    #print(result1)
                    try:
                        if int(result1[0]) == 0:
                            # Golongan 1 Bus
                            vtype = 1
                            vtype_koreksi=1
                            #print("GOL 1 BIS")
                            write_log(lokasi_log,"GOL 1 BIS DETECTED FROM CAM1")
                        elif int(result1[0]) == 1:
                            # Golongan 1
                            vtype = 0
                            vtype_koreksi=0
                            #print("GOL 1 Mobil")
                            write_log(lokasi_log,"GOL 1 MOBIL DETECTED FROM CAM1")
                        else:
                            try:
                                result_cam2=model_cam1.predict(f2, conf=0.4,verbose=False)
                                for r in result_cam2:
                                    #print("LIST DARI RESULT CAM 2: "+str(r.boxes.cls.tolist()))
                                    temp_golongan2= r.boxes.cls.tolist()
                                    
                                temp_golongan2.sort()
                                result2 = [x for x in temp_golongan2 if x !=0 and x != 1 and x != 4 and x != 5]
                                #print(result2)
                            except:
                                #print("TIDAK ADA PREDIKSI DARI CAM 2")
                                write_log_error(lokasi_log,"TIDAK ADA PREDIKSI DARI CAM 2")
                                pass
                            # Truck L and Double Two Tire
                            try:
                                if (result1[0] == 4 and result2[0] == 3 and result2[1] == 3):
                                    # Golongan 5
                                    vtype = 5
                                    vtype_koreksi=5
                                    #print("GOL5")
                                    write_log(lokasi_log,"GOL 5 DETECTED FROM CAM2")

                                    # Truck L and Double One Tire
                                elif (result1[0] == 4 and result2[0] == 2 and result2[1] == 2):
                                    # Check Cam 3
                                    result_cam3=model_cam23.predict(f3, conf=0.4,verbose=False)
                                    for r in result_cam3:
                                        #print("LIST DARI RESULT CAM 3: "+str(r.boxes.cls.tolist()))
                                        temp_golongan3= r.boxes.cls.tolist()
                                        
                                    temp_golongan3.sort()
                                    result3 = [x for x in temp_golongan3 if x !=0 and x != 1 and x != 4 and x != 5]
                                    #print(result3)
                                    if 2 in result3:
                                        vtype = 5
                                        vtype_koreksi=5
                                        #print("GOL 5 VIA CAM 3")
                                        write_log(lokasi_log,"GOL 5 DETECTED FROM CAM3")
                                    else:
                                        vtype = 4
                                        vtype_koreksi=4
                                        #print("GOL 4")
                                        write_log(lokasi_log,"GOL 4 DETECTED FROM CAM3")


                                elif (result1[0] == 4 and result2[0] == 2 and result2[1] == 3):
                                    
                                    result_cam3=model_cam23.predict(f3, conf=0.4,verbose=False)
                                    for r in result_cam3:
                                        #print("LIST DARI RESULT 3: "+str(r.boxes.cls.tolist()))
                                        temp_golongan3= r.boxes.cls.tolist()
                                    
                                    temp_golongan3.sort()
                                    result3 = [x for x in temp_golongan3 if x !=0 and x != 1 and x != 4 and x != 5]
                                    #print(result3)
                                    
                                    if 3 in result3:
                                        vtype = 4
                                        vtype_koreksi=4
                                        #print("GOL 4 VIA CAM 3")
                                        write_log(lokasi_log,"GOL 4 DETECTED FROM CAM3")
                                    else:
                                        vtype = 5
                                        vtype_koreksi=5
                                        print("GOL 5")
                                        write_log(lokasi_log,"GOL 5 DETECTED FROM CAM3")
                            except:
                                #print("bukan golongan 4 atau 5")
                                write_log_error(lokasi_log,"NOT GOLONGAN 4 OR 5")
                                pass

                    # Truck L and Two Tire
                            if ((result1[0] == 4 and result2[0] == 3) and (vtype != 4 and vtype != 5)):
                            # Golongan 3, coba tambahkan one tire, one tire untuk kasus golongan 3 yang heran. untuk golongan 4 gandeng, prioritas cam 3 deteksi sorting one tire, one tire.
                                    vtype = 3
                                    vtype_koreksi=3
                                    #print("GOL 3")
                                    write_log(lokasi_log,"GOL 3 DETECTED FROM CAM2")

                            elif ((result1[0] == 4 and result2[0] == 2) and (vtype != 4 and vtype != 5)):
                                # Golongan 3, coba tambahkan one tire, one tire untuk kasus golongan 3 yang heran. untuk golongan 4 gandeng, prioritas cam 3 deteksi sorting one tire, one tire.
                                vtype = 2
                                
                                #print("GOL 2")
                                write_log(lokasi_log,"GOL 2 DETECTED FROM CAM2")

                                result_cam4=model_cam4.predict(f4, conf=0.4,verbose=False)

                                #print(result_cam4)

                                for r in result_cam4:
                                    #print("LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                                    temp_golongan4= r.boxes.cls.tolist()

                                f4= result_cam4[0].plot(line_width=1, labels=True, conf=True)
                                # cv2.imshow('CAM deteksi cam4', f4)
                                
                                #KOREKSI AI JADI GOL 1
                                #print(str(temp_golongan4))
                                if 1 in temp_golongan4: 
                                    vtype = 2
                                    vtype_koreksi = 2
                                    #print("GOL 2")
                                    write_log(lokasi_log,"GOL 2 DETECTED FROM CAM2")
                                elif 0 in temp_golongan4: 
                                    vtype = 2
                                    vtype_koreksi = 2
                                    #print("GOL 2")
                                    write_log(lokasi_log,"GOL 2 DETECTED FROM CAM2")
                                elif 2 in temp_golongan4:
                                    # Golongan 0
                                    vtype = 0
                                    vtype_koreksi = 0
                                    #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK")
                                    write_log(lokasi_log,"GOL 2 DETECTED CORRECTED TO TRUK GOL 1 BY AI")
                                elif not temp_golongan4:
                                    vtype = 0
                                    vtype_koreksi = 0
                                    #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK")
                                    write_log(lokasi_log,"GOL 2 DETECTED CORRECTED TO TRUK GOL 1 BY AI")
                                #print("GOL 2 BERUBAH MENJADI: " + str(vtype))
                                
                        # Truck L or Truck S
                            elif ((result1[0] == 5 or result1[0] == 4) and (vtype != 4 and vtype != 5)):
                                # tanpa cam4
                                #print("KESINI 5 ATAU 4, LOGIC GOL 2")
                                vtype=2
                                
                                result_cam4=model_cam4.predict(f4, conf=0.4,verbose=False)

                                #print(result_cam4)

                                f4= result_cam4[0].plot(line_width=1, labels=True, conf=True)
                                # cv2.imshow('CAM deteksi cam4', f4)


                                for r in result_cam4:
                                    #print("LIST DARI RESULT 4: "+str(r.boxes.cls.tolist()))
                                    temp_golongan4= r.boxes.cls.tolist()
                                
                                #KOREKSI AI JADI GOL 1
                                #print(str(temp_golongan4))
                                if 1 in temp_golongan4: 
                                    vtype=2
                                    vtype_koreksi=2
                                    #print("GOL 2")
                                    write_log(lokasi_log,"GOL 2 DETECTED FROM CAM2")
                                elif 0 in temp_golongan4: 
                                    vtype=2
                                    vtype_koreksi=2
                                    #print("GOL 2")
                                    write_log(lokasi_log,"GOL 2 DETECTED FROM CAM2")
                                elif 2 in temp_golongan4:
                                    # Golongan 0
                                    vtype=0
                                    vtype_koreksi=0
                                    #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK SINGLE TIRE")
                                    write_log(lokasi_log,"GOL 2 DETECTED CORRECTED TO TRUK GOL 1 BY AI")

                                elif not temp_golongan4:
                                    vtype=0
                                    vtype_koreksi=0
                                    #print("GOL 2 KOREKSI OLEH AI JADI 1 TRUK TIDAK TERDETEKSI")
                                    write_log(lokasi_log,"GOL 2 DETECTED CORRECTED TO TRUK GOL 1 BY AI")
                                
                    except:
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


                    img1 = (
                        datapath
                        + "/"
                        + str(vtype_koreksi)
                        + "/"
                        + time_image
                        + "-"
                        + str(vtype)
                        + "-"
                        + str(vtype_koreksi)
                        + "-"
                        + "cam1.jpg"
                    )
                    img2 = (
                        datapath
                        + "/"
                        + str(vtype_koreksi)
                        + "/"
                        + time_image
                        + "-"
                        + str(vtype)
                        + "-"
                        + str(vtype_koreksi)
                        + "-"
                        + "cam2.jpg"
                    )
                    img3 = (
                        datapath
                        + "/"
                        + str(vtype_koreksi)
                        + "/"
                        + time_image
                        + "-"
                        + str(vtype)
                        + "-"
                        + str(vtype_koreksi)
                        + "-"
                        + "cam3.jpg"
                    )

                    img4 = (
                        datapath
                        + "/"
                        + str(vtype)
                        + "/"
                        + time_image
                        + "-"
                        + str(vtype)
                        + "-"
                        + str(vtype_koreksi)
                        + "-"
                        + "cam4.jpg"
                    )
                    img5 = (
                        datapath
                        + "/"
                        + str(vtype)
                        + "/"
                        + time_image
                        + "-"
                        + str(vtype)
                        + "-"
                        + str(vtype_koreksi)
                        + "-"
                        + "cam5.jpg"
                    )

                    # cv2.imwrite(img1, f1)
                    # cv2.imwrite(img2, f2)
                    # cv2.imwrite(img3, f3)
                    # cv2.imwrite(img4, f4)
                    #cv2.imwrite(img5, f5)
                    #print("berhasil saved f5")
                    #img_path=time_image+ "-"+ str(vtype)+ "-"+ str(vtype_koreksi)+ "-"+ "cam1.jpg"
                    img_path=time_image+ "-"+ str(vtype)+ "-"+ str(vtype_koreksi)
                    #print(img_path)

    #                 class ImageData(BaseModel):
    # base64_data: str
    # golongan: str
    # golongan_koreksi: str
    # waktu: str
    # tipe_cam: str
                    try :
                        url_ping = endpoint_raspberry+"/avc/ping"  # Replace with the actual API URL
                        
                        # Send a GET request to the URL
                        response = requests.get(url_ping)
                        
                        # Check if the request was successful (status code 200)
                        try:
                            if response.status_code == 200:
                                write_log(lokasi_log,"PING TO RASPBERRY SUCCESSED")
                                # # Parse the JSON data from the response
                                # data = response.json()
                                # print(data)
                                
                                # tmpid_gardu="?idgardu="+str(id_gardu)
                                # tmpgolongan="&golongan="+str(vtype_koreksi)
                                # tmpwaktu="&waktu="+str(time_image)
                                # tmpimgpath="&imgpath="+str(img_path)
                                
                                # TMPAPI_ENDPOINT=API_ENDPOINT+tmpid_gardu+tmpgolongan+tmpwaktu+tmpimgpath
                                
                                # # sending post request and saving response as response object
                                # print(id_gardu)
                                # r = requests.post(url=TMPAPI_ENDPOINT)
                                
                                # print(datetime())
                                # print(r.json())

                                ## present new
                                present_avc(id_gardu,vtype_koreksi,time_detect,img_path,endpoint_raspberry)
                                write_log(lokasi_log,"PRESENT TO RASPBERRY SUCCESSED")

                                ## Send image api
                                try:
                                    send_image(base64_data_cam1,str(vtype),str(vtype_koreksi),time_image,"1",endpoint_raspberry)
                                    write_log(lokasi_log,"PRESENT IMAGE CAM 1 TO RASPBERRY SUCCESSED")
                                    send_image(base64_data_cam2,str(vtype),str(vtype_koreksi),time_image,"2",endpoint_raspberry)
                                    write_log(lokasi_log,"PRESENT IMAGE CAM 2 TO RASPBERRY SUCCESSED")
                                    send_image(base64_data_cam3,str(vtype),str(vtype_koreksi),time_image,"3",endpoint_raspberry)
                                    write_log(lokasi_log,"PRESENT IMAGE CAM 3 TO RASPBERRY SUCCESSED")
                                    send_image(base64_data_cam4,str(vtype),str(vtype_koreksi),time_image,"4",endpoint_raspberry)
                                    write_log(lokasi_log,"PRESENT IMAGE CAM 4 TO RASPBERRY SUCCESSED")
                                    
                                except:
                                    #print(f"ERROR KIRIM GAMBAR")
                                    write_log_error(lokasi_log,"FAILED PRESENT IMAGE CAM 1 TO RASPBERRY SUCCESSED")
                                    pass

                                ## update to db
                                try:
                                    update_to_db(img_path,str(vtype),str(vtype_koreksi),time_detect,endpoint_raspberry)
                                    #print(f"BERHASIL UPDATE DB")
                                    write_log(lokasi_log,"UPDATE TO DB SUCCESSED")
                                except:
                                    #print(f"ERROR UPDATE DB")
                                    write_log_error(lokasi_log,"FAILED UPDATE TO DB SUCCESSED")
                                    pass
                            else:
                                #print(f"Request failed with status code: {response.status_code}")
                                write_log_error(lokasi_log,"FAILED REQUEST"+str(response.status_code))
                                pass
                        except:
                            pass
                    except:
                        #print(f"cannot ping to raspberry")
                        write_log_error(lokasi_log,"CANNOT PING TO RASPBERRY")
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
        # cv2.imshow('CAM LIVE', frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    else :
        write_log_error(lokasi_log,"CAM 1 OFF")
        stopthread = True
        time.sleep(3)
        write_log(lokasi_log,f"CAM 2 {p2.is_alive()}")
        write_log(lokasi_log,f"CAM 3 {p3.is_alive()}")
        write_log(lokasi_log,f"CAM 4 {p4.is_alive()}")
        write_log(lokasi_log,f"CAM 5 {p5.is_alive()}")
        write_log_error(lokasi_log,"FORCE EXIT CAUSED CAM 1 OFF")
        exit()
        break

cap.release()
cv2.destroyAllWindows()
write_log_error(lokasi_log,"CAM 1 OFF")
stopthread = True
time.sleep(3)
write_log(lokasi_log,f"CAM 2 {p2.is_alive()}")
write_log(lokasi_log,f"CAM 3 {p3.is_alive()}")
write_log(lokasi_log,f"CAM 4 {p4.is_alive()}")
write_log(lokasi_log,f"CAM 5 {p5.is_alive()}")
write_log_error(lokasi_log,"FORCED CLOSED APP")
exit()