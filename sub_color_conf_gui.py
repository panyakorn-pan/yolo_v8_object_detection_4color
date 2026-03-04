import zmq
from tkinter import *
from tkinter import messagebox

context = zmq.Context()
socket = context.socket(zmq.SUB)
# ฝั่ง Subscriber เป็นคนขอเชื่อมต่อ (Connect)
socket.connect("tcp://localhost:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, "data_topic")

def capture_data():
    last_msg = None
    try:
        # วนลูปดึงค่าล่าสุดออกมาให้หมดเพื่อป้องกัน Queue ค้าง
        while True:
            try:
                raw_msg = socket.recv_string(flags=zmq.NOBLOCK)
                last_msg = raw_msg
            except zmq.Again:
                break
        
        if last_msg:
            _, content = last_msg.split(" ", 1)
            val, text = content.split("|")
            lbl_number.config(text=f"ตัวเลขที่รับมา: {val}")
            lbl_text.config(text=f"ข้อความที่รับมา: {text}")
        else:
            messagebox.showinfo("แจ้งเตือน", "ไม่มีข้อมูลใหม่ส่งมา")
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")

root = Tk()
root.title("Subscriber (Receiver)")
root.geometry("300x200")

lbl_number = Label(root, text="ตัวเลข: --", font=("Tahoma", 12))
lbl_number.pack(pady=10)
lbl_text = Label(root, text="ข้อความ: --", font=("Tahoma", 12))
lbl_text.pack(pady=10)

Button(root, text="Capture ข้อมูล", command=capture_data, bg="lightblue").pack(pady=20)

root.mainloop()