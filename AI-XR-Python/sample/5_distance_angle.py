import cv2
import mediapipe as mp
import math

# MediaPipeのセットアップ
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 既知の身長（仮定）
KNOWN_HEIGHT = 170  # cm

# カメラの水平視野角（仮定）
FOV_HORIZONTAL = 70  # 度

# カメラ映像を取得
cap = cv2.VideoCapture(0)

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

        # 左足首に赤の円を描画
        cv2.circle(frame, (left_ankle_x, left_ankle_y), 10, (0, 0, 255), -1)  # 赤

        # 右足首に赤の円を描画
        cv2.circle(frame, (right_ankle_x, right_ankle_y), 10, (0, 0, 255), -1)  # 赤

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
        
        diff_z, diff_x = -distance * math.sin(math.radians(horizontal_angle)) / 10, distance / 10
        print(diff_z, diff_x)

    # 映像を表示
    cv2.imshow('MediaPipe Pose', frame)

    # 'q'を押すと終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()