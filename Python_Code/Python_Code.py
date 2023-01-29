import cv2
import cvzone
import time
import random
from cvzone.HandTrackingModule import HandDetector
import paho.mqtt.client as mqtt
import numpy as np

def on_connect(client, userdata, flags, rc):
  print("Connection returned result: " + str(rc))

def on_disconnect(client, userdata, rc):
  if rc != 0:
    print('Unexpected Disconnect')
  else:
    print('Expected Disconnect')

def on_message(client, userdata, message):
  print('Received message: "' + str(message.payload) + '" on topic "' +
        message.topic + '" with QoS ' + str(message.qos))

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect_async("test.mosquitto.org")
client.loop_start()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
x = [1, 2, 3]
curIndex = 1
numOfPositions = 1
size = len(x)
count = 0
WL = False

detector = HandDetector(maxHands=1)

timer = 0
stateResult = False
stateWinner = False
startGame = False
playAgain = True
Draw = False
scores = [0, 0]  # [AI, Player]
prev_scores = [0, 0]

client.publish("arduino/simple/win", 1, qos=1)

while True:
    imgBG = cv2.imread("Resources/bg.png")
    success, img = cap.read()

    # scaling bg image and our video
    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Find Hands
    hands, img = detector.findHands(imgScaled)

    if scores[0] == 3 or scores[1] == 3:
        stateWinner = True
        playAgain = False

    # Game
    if startGame:
        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (620, 315), cv2.FONT_HERSHEY_PLAIN, 4, (21, 166, 214), 6)

            if timer > 3:
                stateResult = True
                timer = 0

                if count == 0:
                        i = 1
                        randomNumber = x[i]
                        count = count + 1
                elif Draw:
                    print(count)
                    if count == 1:
                        curIndex = i
                        count = count + 1
                    elif not WL:
                        curIndex = newLeftShiftIndex
                    else:
                        curIndex = newRightShiftIndex
                    newRightShiftIndex = (curIndex + numOfPositions) % size
                    randomNumber = x[newRightShiftIndex]
                    WL = True
                elif (scores[0] <= prev_scores[0]) or (scores[0] > prev_scores[0]):
                    if count == 1:
                        curIndex = i
                        count = count + 1
                    elif WL:
                        curIndex = newRightShiftIndex
                    else:
                        curIndex = newLeftShiftIndex
                    newLeftShiftIndex = (curIndex + (size-(numOfPositions % size))) % size
                    randomNumber = x[newLeftShiftIndex]
                    WL = False
                else:
                    pass

                client.publish("arduino/simple/lemur", randomNumber, qos=1)

                if hands:
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1
                    elif fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2
                    elif fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3
                    else:
                        playerMove = 4
                        if count > 0:
                            count -= 1

                    # randomNumber = random.randint(1, 3)
                    if (playerMove == 4):
                        imgAI = cv2.imread(f'Resources/crossmark.png', cv2.IMREAD_UNCHANGED)
                    else:
                        imgAI = cv2.imread(f'Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)

                    # Player Wins
                    if (playerMove == 1 and randomNumber == 3) or \
                            (playerMove == 2 and randomNumber == 1) or \
                            (playerMove == 3 and randomNumber == 2):
                        Draw = False
                        prev_scores[1] = scores[1]
                        scores[1] += 1

                    # AI Wins
                    if (playerMove == 3 and randomNumber == 1) or \
                            (playerMove == 1 and randomNumber == 2) or \
                            (playerMove == 2 and randomNumber == 3):
                        Draw = False
                        prev_scores[0] = scores[0]
                        scores[0] += 1
                    
                    # Draw
                    if (playerMove == 1 and randomNumber == 1) or \
                            (playerMove == 2 and randomNumber == 2) or \
                            (playerMove == 3 and randomNumber == 3):
                        Draw = True

    imgBG[233:653, 795:1195] = imgScaled

    if stateResult:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))
    
    if stateWinner and playAgain is False:
        if scores[0] > scores[1]:
            cv2.putText(imgBG, "Game Over. AI Won!", (390, 80), cv2.FONT_HERSHEY_DUPLEX, 1.6, (15, 15, 15), 5)
            cv2.putText(imgBG, "Chess Not Unlocked! Press 'r' to play again.", (290, 120), cv2.FONT_HERSHEY_DUPLEX, 1, (15, 15, 15), 4)
        else:
            cv2.putText(imgBG, "Game Over. You Won!", (355, 80), cv2.FONT_HERSHEY_DUPLEX, 1.6, (15, 15, 15), 5)
            cv2.putText(imgBG, "Chess Unlocked! Press 'r' to play again.", (320, 120), cv2.FONT_HERSHEY_DUPLEX, 1, (15, 15, 15), 4)
            client.publish("arduino/simple/win", 4, qos=1)

    else:
        cv2.putText(imgBG, "In order to unlock chest, you must win against an AI in", (180, 55), cv2.FONT_HERSHEY_DUPLEX, 1, (15, 15, 15), 4)
        cv2.putText(imgBG, "a game of roshambo. Player who scores 3 wins.", (205, 85), cv2.FONT_HERSHEY_DUPLEX, 1, (15, 15, 15), 4)
        cv2.putText(imgBG, "Press 's' to start each round of roshambo.", (280, 115), cv2.FONT_HERSHEY_DUPLEX, 1, (15, 15, 15), 4)

    cv2.putText(imgBG, str(scores[0]), (560, 530), cv2.FONT_HERSHEY_PLAIN, 4, (48, 48, 227), 6)
    cv2.putText(imgBG, str(scores[1]), (677, 530), cv2.FONT_HERSHEY_PLAIN, 4, (53, 166, 18), 6)

    # cv2.imshow("Image", img)
    cv2.imshow("BG", imgBG)
    # cv2.imshow("Scaled", imgScaled)

    key = cv2.waitKey(1)
    if key == ord('s'):
        startGame = True
        initialTime = time.time()
        stateResult = False
    elif key == ord('r'):
        playAgain = True
        scores[0] = 0
        scores[1] = 0
        curIndex = 1
        count = 0
        WL = False
        client.publish("arduino/simple/win", 1, qos=1)
    elif key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        client.loop_stop()
        client.disconnect()
        break

