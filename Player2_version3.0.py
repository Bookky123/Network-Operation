from socket import *

# ขั้นตอนการ setting IP Adress, Port
serverName = '192.168.1.101'
serverPort = 12367
clientSocket = socket(AF_INET, SOCK_STREAM)

# function นี้ ใช้เพื่อตรวจสอบตัวเลข ว่าตรงกับ random_number รึเปล่า
def check_sentence(sentences, random_numbers):
    sentence_str = str(sentences)
    random_str = str(random_numbers)
    correct_digits = 0
    correct_digits_wrong_position = 0


# function การปิด connection
def close_connection():
    clientSocket.close()
    print("Connection closed.")

# สร้าง try: เพื่อเช็ค connect ในระหว่าง ที่ทายเลข ถ้าเกิด error ระหว่างเล่นเกม จะหยุดการทำงานทันที เเละ close.connect
try:
    print(f"Trying to connect to {serverName} on port {serverPort}...") # show server name & server port
    clientSocket.connect((serverName, serverPort)) # การเชื่อมต่อ client กับ server
    print("Connected to the game server!")

    while True: #loop ไม่สิ้นสุด เพื่อรับข้อมูลจาก server ซํ้าๆ
        message = clientSocket.recv(1024).decode() # คำสั่งสำหรับใช้ รับข้อมูลจากเซิฟเวอร์ ผ่าน socket.connect


        if not message: # ถ้าไม่ได้รับข้อความ จะ connect lost
            print("Connection lost from server.")
            break

        if message.strip(): # ใช้เพื่อลบช่องว่างทั้ง หน้า เเละ หลัง ของ message
            print(message)

        if "Correct!" in message or "exceeded" in message:
            break # สร้างเพื่อตรวจสอบว่า server ได้ส่งคำว่า Correct or exceeded ถ้าส่งกลับมาเเสดงว่า เกมจบเเล้ว

        if "Game Over" in message:
            break # ถ้า server ส่งข้อความนี้มาจะ Game Over เเละออกจาก loop

        if "Player 2" in message: # ถ้ามีคำว่า Player 2 จะเเสดง output ดังนี้
            print(f"Player 2's guess results: {message}")

        # ถ้า ได้รับข้อมความ 'Your turn' จะเข้า while loop
        if "Your turn" in message:

            while True: # เป็นขั้นตอนการเล่นเกม โดย
                guess = input("Enter your answers (6-digit number): ") #ทายเลข 6 หลัก

                if guess.isdigit() and len(guess) == 6: # ถ้าเดาเลข ไม่เท่ากับ 6 หลัก จะให้เดาใหม่
                    break
                else: # ถ้าเดาเลข 6 หลักครบ จะออกจาก loop เเละ print(" ")
                    print("Invalid input. Please enter exactly 6 digits (numbers only).")

            clientSocket.send(guess.encode()) # หยุดการส่งข้อความ

# ส่วนนี้จะจัดการ error โดย Exception เป็นคราสที่ควบคุม error ทุกประเภท ใน try:
except Exception as e:
    print(f"An error occurred: {e}")

# ส่วนนี้จะทำงานทันทีหลังจาก เจอ error เเละหยุด try: จะปิดการเชื่อมต่อ
finally:
    close_connection()