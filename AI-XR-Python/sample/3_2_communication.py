import socket
import cv2
import mediapipe as mp
import numpy as np
import time

host, port = "127.0.0.1", 25001

# MediaPipeの初期化
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# Webカメラの設定
cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# ソケットオブジェクトを作成します。(IPv4, TCPを使う事を指定)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    # 指定したホストとポートに接続 (1回だけ)
    sock.connect((host, port))
    
    prev_data = "-2"
    
    while (cap.isOpened()):
        ret, frame = cap.read()
        if (not ret):
            print("カメラのフレームを取得できませんでした。")
            break

        # フレームをRGBに変換（MediaPipeはRGB入力を要求）
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 顔ランドマークを取得
        results = face_mesh.process(frame_rgb)
        
        data: str
        # ランドマークが検出された場合
        if (results.multi_face_landmarks):
            for face_landmarks in results.multi_face_landmarks:
                # ランドマークを描画
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_CONTOURS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1),
                )

                # ランドマークの位置を取得
                landmarks = face_landmarks.landmark
                
                # 左目（ランドマーク33）と右目（ランドマーク263）の座標を取得
                left_eye = np.array([landmarks[33].x, landmarks[33].y, landmarks[33].z])
                right_eye = np.array([landmarks[263].x, landmarks[263].y, landmarks[263].z])
                nose_tip = np.array([landmarks[1].x, landmarks[1].y, landmarks[1].z])  # 鼻先

                # 左右の目と鼻先を用いて顔の向きを判定
                if nose_tip[0] < left_eye[0]:  # 鼻が左目より左にある場合
                    data = "2"   # facing right
                elif nose_tip[0] > right_eye[0]:  # 鼻が右目より右にある場合
                    data = "0"   # facing left
                else:
                    data = "1"   # facing Front

                # 判定結果を表示
                cv2.putText(frame, data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # ランドマークが検出されなかった場合
        else:
            data = "-1"
        
        # socket通信を行う
        if (prev_data != data):
            sock.sendall(data.encode("utf-8"))
        # response = sock.recv(1024).decode("utf-8")   # サーバーからのレスポンスを受信する
        # print(response)
        
        # 1秒間隔でデータを送信
        # time.sleep(5)   # n秒間隔でdataを送信する
        
        # prev_dataを更新
        prev_data = data

        # フレームを表示
        cv2.imshow('MediaPipe Face Mesh', frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


finally:
    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()
    sock.close()  # 最後にソケットを閉じる