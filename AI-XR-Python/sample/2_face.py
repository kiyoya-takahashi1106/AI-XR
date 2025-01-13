import cv2
import mediapipe as mp
import numpy as np

# MediaPipeの初期化
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# Webカメラの設定
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("カメラのフレームを取得できませんでした。")
        break

    # フレームをRGBに変換（MediaPipeはRGB入力を要求）
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 顔ランドマークを取得
    results = face_mesh.process(frame_rgb)

    # ランドマークが検出された場合
    if results.multi_face_landmarks:
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
                direction = "facing left"
            elif nose_tip[0] > right_eye[0]:  # 鼻が右目より右にある場合
                direction = "facing Right"
            else:
                direction = "facing Front"

            # 判定結果を表示
            cv2.putText(frame, direction, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # フレームを表示
    cv2.imshow('MediaPipe Face Mesh', frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()