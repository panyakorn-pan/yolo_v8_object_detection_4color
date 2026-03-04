# yolov8n_detection.py
# ใช้ YOLOv8n (nano) ตรวจจับวัตถุแบบ real-time พร้อมวาดกรอบและ label

import cv2
from ultralytics import YOLO

# โหลดโมเดล YOLOv8 nano (เล็กที่สุด เร็วที่สุด เหมาะกับ real-time บนเครื่องทั่วไป)
model = YOLO("best.pt")

# เปิดกล้อง
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ ไม่สามารถอ่านภาพจากกล้องได้")
        break

    # ตรวจจับวัตถุในภาพ → ได้กล่องทั้งหมดใน batch แรก
    results = model(frame)[0]

    # วนลูปผ่านกล่องที่ตรวจพบ
    for box in results.boxes:
        conf = float(box.conf[0])        # ค่า confidence (0.0 - 1.0)
        if conf >= 0.75 :

            x1, y1, x2, y2 = map(int, box.xyxy[0])  # มุมซ้ายบนถึงขวาล่าง
            cls_id = int(box.cls[0])                # หมายเลขคลาส (เช่น 0 = person)
            
            label = f"{model.names[cls_id]} {conf:.2f}"
            color = (0, 255, 255)                   # สีกรอบ (เหลือง)
            color2 = (0, 0, 255)                   # สีกรอบ (เหลือง)
        

            # 🖍️ วาดกรอบรอบวัตถุ
            # cv2.rectangle(image, pt1, pt2, color, thickness)
            # - pt1: พิกัดมุมบนซ้าย (x1, y1)
            # - pt2: พิกัดมุมล่างขวา (x2, y2)
            # - color: สีของกรอบ (B, G, R)
            # - thickness: ความหนาของเส้น (2 พิกเซล)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # 🏷️ แสดงชื่อวัตถุบนภาพ
            # cv2.putText(image, text, org, font, scale, color, thickness)
            # - text: ข้อความที่จะแสดง
            # - org: ตำแหน่งเริ่มวาด (x1, y1 - 10) = เหนือกรอบเล็กน้อย
            # - font: แบบอักษร (FONT_HERSHEY_SIMPLEX = อ่านง่าย)
            # - scale: ขนาดตัวอักษร (0.6 = กลางๆ)
            # - color: สีของตัวอักษร
            # - thickness: ความหนาของตัวอักษร (2 พิกเซล)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color2, 2)

    cv2.imshow("YOLOv8n Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()