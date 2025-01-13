import socket

host, port = "127.0.0.1", 25001

# 送るデータ
data = "-3,5,-3"

# ソケットオブジェクトを作成します。(IPv4, TCPを使う事を指定)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # 指定したホストとポートに接続 (1回だけ)
    sock.connect((host, port))
    
    for i in range(20):   # 20回繰り返す
        sock.sendall(data.encode("utf-8"))   # サーバーにデータを送信する
        response = sock.recv(1024).decode("utf-8")    # サーバーからのレスポンスを受信する
        print(response)

finally:
    sock.close()  # 最後にソケットを閉じる
