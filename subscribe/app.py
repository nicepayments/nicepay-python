from flask import Flask, render_template, request
from Crypto.Cipher import AES
from requests.auth import HTTPBasicAuth
import requests
import uuid
import json

clientId = 'S2_af4543a0be4d49a98122e01ec2059a56'
secretKey = '9eb85607103646da9f9c02b128f2e5ee'

key = secretKey[:32]
iv = secretKey[:16]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        'regist.html'
    )

@app.route('/regist', methods=['POST'])
def regist():
    plainText = [] 
    plainText.append("cardNo=" + request.form['cardNo'])
    plainText.append("&expYear=" + request.form['expYear'])
    plainText.append("&expMonth=" + request.form['expMonth'])
    plainText.append("&idNo=" + request.form['idNo'])
    plainText.append("&cardPw=" + request.form['cardPw'])
    plainText = ''.join(plainText)

    try:
        response = requests.post('https://sandbox-api.nicepay.co.kr/v1/subscribe/regist', 
            json={
                'encData': encrypt(plainText, key, iv),
                'orderId': str(uuid.uuid4()),
                'encMode': 'A2'
            },
            headers={
                'Content-type' : 'application/json'
            },
            auth=HTTPBasicAuth(clientId, secretKey)
        )
        
        resDict = json.loads(response.text)
        print(resDict)
        billing(resDict['bid'])
        expire(resDict['bid'])
        return render_template(
            'response.html',
            resultMsg = resDict['resultMsg']
        )

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return render_template(
        'response.html',
        resultMsg = plainText
    )


def billing(bid):
    try:
        response = requests.post('https://sandbox-api.nicepay.co.kr/v1/subscribe/' + bid + '/payments', 
            json={
                'orderId': str(uuid.uuid4()),
                'amount': 1004,
                'goodsName': "card billing test",
                'cardQuota': 0,
                'useShopInterest': False
            },
            headers={
                'Content-type' : 'application/json'
            },
            auth=HTTPBasicAuth(clientId, secretKey)
        )
        
        resDict = json.loads(response.text)
        print(resDict)

        return resDict
        
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def expire(bid):
    try:
        response = requests.post('https://sandbox-api.nicepay.co.kr/v1/subscribe/' + bid + '/expire', 
            json={
                'orderId': str(uuid.uuid4())
            },
            headers={
                'Content-type' : 'application/json'
            },
            auth=HTTPBasicAuth(clientId, secretKey)
        )
        
        resDict = json.loads(response.text)
        print(resDict)

        return resDict
        
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def encrypt(text, key, iv):
    pad = lambda s : s+chr(16-len(s)%16)*(16-len(s)%16)
    raw = pad(text)
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    return cipher.encrypt(raw.encode("utf8")).hex()

if __name__ == '__main__':
    app.run(debug=True)