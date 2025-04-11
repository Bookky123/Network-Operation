from socket import *
import random
import threading
import  time

# setting serverPort , serverIP
serverPort = 12367
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('192.168.1.17', serverPort))
serverSocket.listen()

print('THE GAME')

# function นี้ ใช้เพื่อตรวจสอบตัวเลข ว่าตรงกับ random_number รึเปล่า
def check_sentence(sentences, random_numbers):
    sentence_str = str(sentences)
    random_str = str(random_numbers)
    correct_digits = 0
    correct_digits_wrong_position = 0

    # for loop สำหรับตรวจว่าเลขถูกรึเปล่า
    for m in range(len(sentence_str)): # สร้าง loop นับจาก sentence
        if sentence_str[m] == random_str[m]:
            correct_digits += 1 # โดย sentenceตำเเหน่งที่ m จะ+1 เมื่อ เลขถูกตำเเหน่ง
        elif sentence_str[m] in random_str:
            correct_digits_wrong_position += 1 # โดย ตำเเหน่งที่ m จะ+1 เมื่อมีเลขอยู่ random_number

    # จากนั้น จะส่งค่าออกมา
    return correct_digits, correct_digits_wrong_position

# function นี้จะ เป็นการ random เลข 6 ตำเเหน่ง เเละไม่ซํ้ากัน
def generate_random_6digit_number():
    digits = random.sample(range(10), 6)
    return int(''.join(map(str, digits)))

# output จะเป็น random_number
random_number = generate_random_6digit_number()
print("Random number:", random_number)

players = []

# function นับเวลาถอยหลัง ระหว่างรอผู้เล่น
def countdown_timer(event):
    seconds = 30
    while seconds > 0 and not event.is_set():
        if len(players) == num_players: #ถ้า จน.player == num_player จะจบ break
            print("Players have joined, starting the game!")
            break

        print(f"Waiting for players to join... {seconds} seconds remaining")
        time.sleep(1) #ถ้า จน. player ยังไม่ครบ ก็จะนับถอยหลัง จนกว่าจะครบ
        seconds -= 1

    # ต้องเเก้ตรงนี้ ให้สามารถ รันได้โดยไม่ระบุ จน. player
    if seconds == 0 and len(players) != num_players: #ถ้า เวลา = 0 จะเริ่มเกมทันที
        print("Time is up! Starting the game with the current players.")

num_players = 2


while True:
    players_joined_event = threading.Event() # ใช้สำหรับสื่อสาร เพื่อบอกสถานะ player

    # จะทำงานร่วมกับ function countdown_timer & players_join
    countdown_thread = threading.Thread(target=countdown_timer, args=(players_joined_event,))
    countdown_thread.start()

    # loop for สำหรับการเชื่อมต่อ players & จะบันทึก ข้อมูล เป็น[list]
    for i in range(num_players):
        connectionSocket, addr = serverSocket.accept()
        players.append((connectionSocket, addr))
        print(f"Player {i + 1} connected from {addr}")

    # โดย จะเป็นกำหนด รอบผู้เล่น คือ 12 รอบ
    num_guesses_per_player = 12 // num_players
    print(f"Each player gets {num_guesses_per_player} guesses.")


    try:
        game_over = False # เช็คว่าเกมจบรึยัง
        guesses_made = [0] * num_players # เก็บจำนวนการเดาของผู้เล่นแต่ละคน เริ่มต้นที่ 0
        max_rounds = 12 / num_players # จน. players หารด้วย 12 ครั้ง เพื่อกำหนดรอบของเเต่ละ player ได้ชัดเจน
        current_round = 1

        # while loop จนกว่าจะจบเกม
        while not game_over:
            for player_index, (connectionSocket, addr) in enumerate(players): # loopของ เเต่ละ players
                if guesses_made[player_index] < max_rounds: #เช็ครอบของผู้เล่น ว่าเกินรึยัง
                    round_message = f"Your turn , Round: {current_round}"
                    connectionSocket.send(round_message.encode()) #ส่งข้อความไปยังผู้เล่น
                    sentence = connectionSocket.recv(1024).decode() # รับข้อมูลการเดา

                    # ถ้าเกินรอบของผู้เล่น เกมจะจบทันที
                    if current_round > max_rounds:
                        game_over = True
                        break

                    if not sentence:
                        break

                    # ตรวจสอบการเดาของผู้เล่น
                    correct, wrong_position = check_sentence(sentence, random_number)

                    # ถ้า ผู้เล่นเดาถูกทุกตัว
                    if sentence == str(random_number): #เเละจะส่งข้อความไปให้ผู้เล่นทุกคน ว่า ใครทายถูก
                        connectionSocket.send(f"Player {player_index + 1}: Correct! The number was: {sentence}".encode())
                        for j, (cs, _) in enumerate(players):
                            if j != player_index:
                                cs.send(f"Player {player_index + 1} guessed the correct number: {sentence}".encode())
                        game_over = True # จบเกมเมื่อทายถูกทุกตัว
                        break
                    else:
                        # ถ้าทายผิด ให้ส่งข้อความบอก feedback ว่ามีตัวเลขถูกหรืออยู่ผิดตำแหน่งกี่ตัว
                        feedback = (f"\n{correct} {wrong_position} ({sentence})\n"
                                    f"Correct value & position: {correct} "
                                    f" | Correct value but wrong position: {wrong_position}\n-----------------------------------------"
                                    f"-------------------------"
                                    )
                        connectionSocket.send(feedback.encode()) # sent feedback to player
                        guesses_made[player_index] += 1

                #  ถ้าผู้เล่นใช้จำนวนครั้งที่อนุญาตในการเดาครบแล้ว
                if guesses_made[player_index] >= num_guesses_per_player:
                    connectionSocket.send(f"Player {player_index + 1}: You've exceeded the maximum number of guesses.".encode())

            # นับรอบผู้เล่น เมื่อทายเสร็จในรอบนั้น
            current_round += 1

            #ตรวจสอบว่าผู้เล่น ทุกคนทายครบรอบของตัวเองรึยัง
            if all(guesses == max_rounds for guesses in guesses_made):
                break

        # ถ้าเกมจบเเต่ ไม่มีใครทายถูก
        if not game_over:
            for connectionSocket, _ in players:
                connectionSocket.send(f"Game over! The number was: {random_number}".encode())

    # จัดการกับ error ที่อาจเกิด
    except Exception as e:
        print(f"An error occurred: {e}")

    # ปิดการเขื่อมต่อของผู้เล่น เมื่อจบเกม
    finally:
        for connectionSocket, _ in players:
            connectionSocket.close()

    # ปิดเซิฟเวอร์
    serverSocket.close()