import socket
import cv2
import mediapipe as mp
import math
import time

# MediaPipeのセットアップ
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# ソケットの設定
host, port = "127.0.0.1", 25001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

# 既知の身長（仮定）
KNOWN_HEIGHT = 170  # cm

# カメラの水平視野角（仮定）
FOV_HORIZONTAL = 70  # 度

# カメラ映像を取得
cap = cv2.VideoCapture(0)

move_lst = []  # 動いたときはdiff_zの絶対値が4より大きい時(動いた時)はTrueを入れる
move_mode = False  # Trueの時は運動を促進

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("カメラ映像が取得できませんでした。")
            break

        # 映像をRGBに変換
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe Poseによる推論
        results = pose.process(rgb_frame)

        # 推論結果がある場合、ランドマークを取得
        if results.pose_landmarks:
            # フレームの高さと幅を取得
            h, w, _ = frame.shape

            # カメラの中心座標
            cx, cy = w // 2, h // 2

            # ノーズ（頭頂部）
            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            nose_x, nose_y = int(nose.x * w), int(nose.y * h)

            # 頭頂部（ノーズ）に緑の円を描画
            cv2.circle(frame, (nose_x, nose_y), 10, (0, 255, 0), -1)  # 緑

            # 水平方向の角度を計算
            horizontal_angle = ((nose_x - cx) / cx) * FOV_HORIZONTAL

            # 映像に水平角度を表示
            cv2.putText(frame, f"Horizontal Angle: {horizontal_angle:.2f} degrees", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 左足首
            left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
            left_ankle_x, left_ankle_y = int(left_ankle.x * w), int(left_ankle.y * h)

            # 右足首
            right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
            right_ankle_x, right_ankle_y = int(right_ankle.x * w), int(right_ankle.y * h)

            # 足首の平均座標を計算（人の重心に近い）
            avg_ankle_x = (left_ankle_x + right_ankle_x) // 2
            avg_ankle_y = (left_ankle_y + right_ankle_y) // 2

            # ピクセル距離を計算（頭から足まで）
            pixel_distance = math.sqrt((nose_x - avg_ankle_x) ** 2 + (nose_y - avg_ankle_y) ** 2)

            # 実際の距離を計算（仮のスケーリング係数）
            scale_factor = KNOWN_HEIGHT / pixel_distance
            distance = scale_factor * h  # 高さを基準にスケール調整

            # 映像に距離を表示（太字）
            cv2.putText(frame, f"Distance: {distance:.2f} cm", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # 太くするためにthicknessを3に設定

            # X、Z座標の差分を計算
            diff_z, diff_x = -distance * math.sin(math.radians(horizontal_angle)) / 10, distance / 10

            # ソケットでデータを送信
            data = f"{diff_x:.2f},{diff_z:.2f}"
            sock.sendall(data.encode("utf-8"))
            # print(f"Sent: {data}")

            # move_flagを判定
            if abs(diff_z) > 4:
                move_flag = True
            else:
                move_flag = False

            # move_lstの更新
            if len(move_lst) < 20:
                move_lst.append(move_flag)
                print(move_lst)
            else:
                print(move_lst)
                
                # 運動モードの制御
                if move_mode:  # 運動を促進されている時
                    pass
                    
                else:  # 運動モードが開始されていない時
                    move_lst = move_lst[1:] + [move_flag]
                    if (True not in move_lst):
                        move_mode = True  # 動きがあれば運動モード開始
                        # ソケットでデータを送信
                        data = f"modechange_to_True"
                        sock.sendall(data.encode("utf-8"))
                        print("運動促進")

            time.sleep(0.3)  # n秒間隔でdataを送信する

        # 映像を表示
        cv2.imshow('MediaPipe Pose', frame)

        # 'q'を押すと終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()
    sock.close()