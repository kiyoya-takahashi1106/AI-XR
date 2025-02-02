using UnityEngine;

public class CoinScript : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Player")
        {
            Debug.Log("Player collected a coin!");

            // �A�C�e��������
            gameObject.SetActive(false);

            // �R�C�����W��ʒm
            GameObject listener = GameObject.FindFirstObjectByType<PlayerScript>().gameObject;
            listener.GetComponent<PlayerScript>().CollectCoin();
        }
    }
}
