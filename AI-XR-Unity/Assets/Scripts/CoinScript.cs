using UnityEngine;

public class CoinScript : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Player")
        {
            Debug.Log("Player collected a coin!");

            // アイテムを消す
            gameObject.SetActive(false);

            // コイン収集を通知
            GameObject listener = GameObject.FindFirstObjectByType<PlayerScript>().gameObject;
            listener.GetComponent<PlayerScript>().CollectCoin();
        }
    }
}
