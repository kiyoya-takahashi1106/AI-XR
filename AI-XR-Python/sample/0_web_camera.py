import cv2

# Webカメラをキャプチャ（通常0はデフォルトのカメラを指定）
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Webカメラを開くことができませんでした。")
    exit()

while True:
    # フレームを取得
    ret, frame = cap.read()
    if not ret:
        print("フレームを取得できませんでした。")
        break

    # フレームを表示
    cv2.imshow('Web Camera', frame)

    # 'q'キーを押すと終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()
