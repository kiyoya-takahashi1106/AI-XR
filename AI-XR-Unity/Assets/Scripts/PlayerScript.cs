using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;
using System;

public class MyListener : MonoBehaviour
{
    Thread thread;
    public int connectionPort = 25001;
    TcpListener server;
    TcpClient client;
    bool running;
    Vector3 position = Vector3.zero;
    private readonly object positionLock = new object();

    void Start()
    {
        thread = new Thread(GetData)
        {
            IsBackground = true
        };

        server = new TcpListener(IPAddress.Any, connectionPort);
        running = true;
        thread.Start();
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
                            Debug.Log("運動促進 : コインゲーム開始");
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
            return new Vector3(x - 9.9f, 6, z + 7);
        }

        Debug.LogWarning("Invalid coordinate format. Defaulting to (0, 6, 0).");
        return new Vector3(0, 6, 0);
    }

    void Update()
    {
        lock (positionLock)
        {
            transform.position = position;
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
