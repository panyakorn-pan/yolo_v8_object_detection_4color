import cv2
import zmq
from tkinter import *
from PIL import Image, ImageTk
from ultralytics import YOLO

# --- ส่วนการตั้งค่า ZMQ (จาก pub_gui) ---
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555") 

# --- ส่วนการตั้งค่า YOLO (จาก yolov8n_detection) ---
model = YOLO("best.pt")
cap = cv2.VideoCapture(1)

def update_frame():
    ret, frame = cap.read()
    if ret:
        # ตรวจจับวัตถุ
        results = model(frame)[0]
        detected_info = "None|0.00" # ค่าเริ่มต้นถ้าไม่เจออะไร

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf >= 0.75:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                label_name = model.names[cls_id]
                
                # เตรียมข้อมูลเพื่อส่ง (ชื่อวัตถุ|ความเชื่อมั่น)
                detected_info = f"{label_name}|{conf:.2f}"

                # วาดกรอบบนหน้าจอ Preview
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame, f"{label_name} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # ส่งข้อมูลผ่าน ZMQ ทันทีที่ตรวจพบ (อัปเดตค่าล่าสุดเสมอ)
                # หมายเหตุ: sub_gui จะได้รับค่านี้เมื่อกดปุ่ม Capture
                socket.send_string(f"data_topic {detected_info}")

        # แปลงภาพ OpenCV (BGR) เป็น format ที่ Tkinter แสดงผลได้
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

    # เรียกฟังก์ชันตัวเองซ้ำทุก 10ms (เพื่อให้วิดีโอไหลลื่น)
    lbl_video.after(10, update_frame)

# --- ส่วนการสร้าง GUI (ประยุกต์จาก pub_gui) ---
root = Tk()
root.title("YOLOv8 Publisher")
root.geometry("700x600")

Label(root, text="YOLOv8 Real-time Detection (Streaming to SUB)", font=("Tahoma", 12, "bold")).pack(pady=10)

# ส่วนแสดงผลวิดีโอ
lbl_video = Label(root)
lbl_video.pack()

Label(root, text="สถานะ: กำลังส่งข้อมูลไปยัง tcp://*:5555", fg="green").pack(pady=10)

# เริ่มต้นการอ่านเฟรมจากกล้อง
update_frame()

root.mainloop()

# คืนทรัพยากรเมื่อปิดโปรแกรม
cap.release()
cv2.destroyAllWindows()