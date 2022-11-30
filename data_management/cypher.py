
import base64
from data_management.json_store import JsonStore
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class Security:

    def __init__(self, accesskey):
        self.__accesskey = accesskey
        self.__key = self.get_key()
        self.__salt = self.decoded_value("salt")

    def get_key(self):
        key_padder = padding.PKCS7(256).padder()
        key = key_padder.update(self.__accesskey.encode()) + key_padder.finalize()
        return key

    def validate_accesskey(self):
        kdf = Scrypt(salt=self.__salt, length=32, n=2 ** 14, r=8, p=1)
        derivated_accesskey = self.decoded_value("contrasena")
        try:
            kdf.verify(self.__accesskey.encode(), derivated_accesskey)
            return True
        except:
            return False

    # Funcion principal para cifrar los campos del usuario
    def encode_value(self, key, value, iv):
        json = JsonStore()
        mydict = {}
        bytes = value.encode()
        cipher = Cipher(algorithms.AES256(self.__key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        data_padder = padding.PKCS7(128).padder()
        padded_data = data_padder.update(bytes) + data_padder.finalize()
        result = encryptor.update(padded_data) + encryptor.finalize()
        encoded_result = base64.b64encode(result)
        encoded_iv = base64.b64encode(iv)
        mydict[key] = encoded_result.decode("ascii")
        mydict["iv_"+key] = encoded_iv.decode("ascii")
        json.add_item(mydict)

    @staticmethod
    def find_in_json(key):
        json = JsonStore()
        value = json.find_item(key)
        return value

    def decoded_value(self, key):
        value = self.find_in_json(key)
        return base64.b64decode(value)

    def decode_value(self, iv_key, key):
        iv = self.decoded_value(iv_key)
        cipher = Cipher(algorithms.AES256(self.__key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        padded_user_value = self.decoded_value(key)
        value = decryptor.update(padded_user_value) + decryptor.finalize()
        decoded_value = unpadder.update(value) + unpadder.finalize()
        return decoded_value