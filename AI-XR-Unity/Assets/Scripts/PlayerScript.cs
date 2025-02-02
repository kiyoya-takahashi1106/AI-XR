using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;
using System;

public class PlayerScript : MonoBehaviour
{
    Thread thread;
    public int connectionPort = 25001;
    TcpListener server;
    TcpClient client;
    bool running;
    Vector3 position = new Vector3(-5, 6, 7); // �����ʒu��Y���W��6�ɐݒ�
    private readonly object positionLock = new object();

    public GameObject coin; // Unity��ɔz�u����Ă���R�C���I�u�W�F�N�g

    // �Q�[���J�n�t���O�^�J�n�v���t���O
    private bool gameStart = false;
    private bool startGameRequested = false;
    private readonly object startGameLock = new object();

    void Start()
    {
        thread = new Thread(GetData)
        {
            IsBackground = true
        };

        server = new TcpListener(IPAddress.Any, connectionPort);
        running = true;
        thread.Start();

        // �R�C�����\���ɂ���
        if (coin == null)
        {
            // �V�[������ "Coin" �Ƃ������O�̃I�u�W�F�N�g������Ύ擾
            coin = GameObject.Find("Coin");
            if (coin == null)
            {
                Debug.LogError("�R�C���I�u�W�F�N�g��������܂���ł����B");
            }
            else
            {
                coin.SetActive(false); // ������ԂŔ�\��
            }
        }
    }

    void GetData()
    {
        server.Start();
        Debug.Log("Server started, waiting for client...");

        while (running)
        {
            try
            {
                if (client == null || !client.Connected)
                {
                    Debug.Log("Waiting for client connection...");
                    client = server.AcceptTcpClient();
                    Debug.Log("Client connected!");
                }

                Connection();
            }
            catch (SocketException ex)
            {
                Debug.LogError($"SocketException: {ex.Message}");
                break;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Exception in GetData: {ex.Message}");
                break;
            }
        }

        server.Stop();
        client?.Close();
    }

    void Connection()
    {
        try
        {
            using (NetworkStream nwStream = client.GetStream())
            {
                byte[] buffer = new byte[client.ReceiveBufferSize];
                while (running && client.Connected)
                {
                    int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize);
                    if (bytesRead == 0)
                    {
                        Debug.LogWarning("Client disconnected");
                        break;
                    }

                    string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    if (!string.IsNullOrEmpty(dataReceived))
                    {
                        if (dataReceived.Contains("modechange_to_True"))
                        {
                            Debug.Log("�^�����i : �R�C���Q�[���J�n");

                            // �X���b�h��ł͒��ڃI�u�W�F�N�g���삹���A�t���O�Ń��N�G�X�g�𑗂�
                            lock (startGameLock)
                            {
                                startGameRequested = true;
                            }
                        }
                        else
                        {
                            var newPosition = ParseData(dataReceived);
                            lock (positionLock)
                            {
                                position = newPosition;
                            }
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error in Connection: {ex.Message}");
        }
    }

    public static Vector3 ParseData(string data)
    {
        string[] splitData = data.Split(',');
        if (splitData.Length >= 2 &&
            float.TryParse(splitData[0], out float x) &&
            float.TryParse(splitData[1], out float z))
        {
            return new Vector3(x - 9.9f, 6, z + 7); // Y���W���Œ�
        }

        Debug.LogWarning("Invalid coordinate format. Defaulting to (0, 6, 0).");
        return new Vector3(0, 6, 0);
    }

    void Update()
    {
        // �X���b�h����󂯎�����ʒu���𔽉f
        lock (positionLock)
        {
            // ���݂�Y���W��ێ����Ĉʒu���X�V
            transform.position = new Vector3(position.x, transform.position.y, position.z);
        }

        // �X���b�h����́u�Q�[���J�n�v���N�G�X�g������΁A���C���X���b�h�Ŏ��s
        lock (startGameLock)
        {
            if (startGameRequested)
            {
                StartGame();
                startGameRequested = false;
            }
        }
    }

    void StartGame()
    {
        gameStart = true;
        // �R�C����\������
        if (coin != null)
        {
            coin.SetActive(true);
        }
    }

    public void CollectCoin()
    {
        if (gameStart)
        {
            Debug.Log("�R�C���Q�[���I��!!!!");
            gameStart = false;

            // �R�C�����ēx��\���ɂ���
            if (coin != null)
            {
                coin.SetActive(false);
            }

            // ���[�h�ύX���b�Z�[�W�𑗐M
            SendModeChangeMessage("modechange_to_False");
        }
    }

    private void SendModeChangeMessage(string message)
    {
        try
        {
            if (client != null && client.Connected)
            {
                NetworkStream nwStream = client.GetStream();
                if (nwStream != null && nwStream.CanWrite)
                {
                    byte[] messageBytes = Encoding.UTF8.GetBytes(message);
                    nwStream.Write(messageBytes, 0, messageBytes.Length);
                    Debug.Log("Sent message: " + message);
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error sending message: {ex.Message}");
        }
    }

    void OnDestroy()
    {
        running = false;
        try
        {
            server?.Stop();
            client?.Close();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error during cleanup: {ex.Message}");
        }

        if (thread != null && thread.IsAlive)
        {
            thread.Join();
        }
    }
}