import cv2
import mediapipe as mp
import math

# MediaPipeのセットアップ
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 既知の身長（仮定）
KNOWN_HEIGHT = 170  # cm

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

        # ノーズ（頭頂部）
        nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        nose_x, nose_y, nose_z = nose.x * w, nose.y * h, nose.z

        # 左腰
        left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        left_hip_x, left_hip_y, left_hip_z = left_hip.x * w, left_hip.y * h, left_hip.z

        # 右腰
        right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        right_hip_x, right_hip_y, right_hip_z = right_hip.x * w, right_hip.y * h, right_hip.z

        # 腰の平均座標を計算
        avg_hip_x = (left_hip_x + right_hip_x) / 2
        avg_hip_y = (left_hip_y + right_hip_y) / 2
        avg_hip_z = (left_hip_z + right_hip_z) / 2

        # 3Dユークリッド距離を計算（鼻と腰の距離）
        pixel_distance_3d = math.sqrt(
            (nose_x - avg_hip_x) ** 2 +
            (nose_y - avg_hip_y) ** 2 +
            (nose_z - avg_hip_z) ** 2
        )

        # 身長を基準としたスケーリング係数を計算
        full_body_pixel_distance = pixel_distance_3d * 2  # 鼻から腰までの距離を2倍
        scale_factor = KNOWN_HEIGHT / full_body_pixel_distance

        # 実際のカメラからの距離を計算
        distance = scale_factor * h  # 高さを基準にスケール調整

        # 映像に距離を表示
        cv2.putText(frame, f"Distance: {distance:.2f} cm", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # デバッグ用にランドマークを描画
        cv2.circle(frame, (int(nose_x), int(nose_y)), 10, (0, 255, 0), -1)  # 鼻
        cv2.circle(frame, (int(avg_hip_x), int(avg_hip_y)), 10, (255, 0, 0), -1)  # 腰

    # 映像を表示
    cv2.imshow('MediaPipe Pose', frame)

    # 'q'を押すと終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()
