import hashlib
import re
from Crypto.Cipher import AES
import base64
from datetime import datetime, timedelta
import subprocess
import ntplib
import logging

TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
FILE_ENV_CODE = 'toolText.lic'
FILE_LICENSE = 'license.lic'


def get_uuid():
    # run on win7 failed?
    # wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
    # stdin is important
    try:
        sp = subprocess.run('wmic csproduct list full | findstr UUID',
                            shell=True,
                            timeout=10,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
        if sp.returncode == 0:
            return str(sp.stdout, encoding='utf-8').strip().split('=')[1]
    except:
        pass
    return None


def gen_license(env_code, create_time, valid_date, ver='STD'):
    license = f'{env_code},{create_time},{valid_date},{ver}'
    ecb = AESECB()
    return ecb.encrypt(license)


def parasing_license(code):
    ecb = AESECB()
    return ecb.decrypt(code)


def save_env_code(code):
    try:
        with open(FILE_ENV_CODE, 'w', encoding='utf-8') as f:
            f.write(code)
    except:
        return False
    return True


def load_env_code():
    try:
        with open(FILE_ENV_CODE, 'r', encoding='utf-8') as f:
            value = f.read()
    except:
        return None
    return value


def load_license():
    try:
        with open(FILE_LICENSE, 'r', encoding='utf-8') as f:
            value = f.read()
        if value:
            return parasing_license(value)
    except Exception as e:
        logging.error(e)
    return None


def save_license(license):
    try:
        with open(FILE_LICENSE, 'w', encoding='utf-8') as f:
            f.write(license)
            return True
    except:
        pass
    return False


def _is_env_code(code):
    if re.match(r'^[0-9A-F]{32,32}$', code):
        return True
    else:
        return False


def _cal_deadline(start, days):
    start = datetime.strptime(start, TIME_FORMAT)
    end = start + timedelta(days=int(days))
    return end.strftime(TIME_FORMAT)


def get_network_time() -> datetime:
    client = ntplib.NTPClient()
    for server in ['ntp.aliyun.com', 'time.apple.com', 'time.windows.com']:
        try:
            response = client.request(server)
            return datetime.fromtimestamp(response.tx_time)
        except:
            pass


def _is_in_period(start, days, current_time: datetime = None):
    start = datetime.strptime(start, TIME_FORMAT)
    if current_time is None:
        current_time = datetime.now()
    if (start + timedelta(days=int(days))).timestamp() > current_time.timestamp():
        return True
    return False


class AESECB:
    def __init__(self, key='Bert good at python'):
        self._key = key

    def encrypt(self, text):
        key = self._padding(self._key)[0:16]
        b_text = self._padding(text)
        cryptor = AES.new(key, AES.MODE_ECB)
        cipher_text = cryptor.encrypt(b_text)
        return str(base64.b64encode(cipher_text), encoding='utf-8')

    def decrypt(self, text):
        key = self._padding(self._key)[0:16]
        cryptor = AES.new(key, AES.MODE_ECB)
        plain_text = cryptor.decrypt(
            base64.b64decode(bytes(text, encoding='utf-8')))
        return bytes.decode(plain_text).rstrip('\0')

    def _padding(self, text):
        raw_text = text.encode('utf-8')
        rem = len(raw_text) % 16
        if rem:
            add = 16 - rem
            raw_text = raw_text + (b'\0' * add)
        return raw_text


class ExeAuth:
    def __init__(self, exe_name):
        self._exe_name = exe_name
        self.current_env_code = self.gen_env_code()

    def gen_env_code(self):
        md5 = hashlib.md5()
        code = f'{self._exe_name},{get_uuid()}'
        md5.update(code.encode('utf-8'))
        return str(md5.hexdigest()).upper()

    def is_valid_license(self, license, current_time: datetime = None):
        env_code, create_time, valid_date, _ = license.split(',')
        if not env_code == self.current_env_code:
            return False
        if not _is_in_period(create_time, valid_date, current_time):
            return False
        return True


if __name__ == '__main__':
    pass
    ecb = AESECB()
    # e = ecb.encrypt("hello world")
    # d = ecb.decrypt('PFzNt5I7Jz7SEAIU/JCiGzQYRNOuEQPN3AA2ikFvVjV/pCiIyzj/uXGkOmwYKLX3lTk+FqGjM+8eD224KwZ1sA==')
    # print(type(e), e)
    # print(type(d), d)
    # env_code = gen_env_code('ExcelBingo')
    # print(env_code)
    # if check_env_code(env_code):
    #     print('env code is ok')
    # else:
    #     print('wrong env code')
    # print(type(license),license)
    # if save_license_to_reg('ExcelBingo', license):
    #     license = get_license_from_reg('ExcelBingo')
    #     print(type(license),license)
    #     text = parasing_license(license)
    #     print(text)
    # else:
    #     print('Save to register failed')

    # print(parasing_license(
    #     'IWPVq5BeaqHJJjjfTQO1fiappxcXPcdwG9ca37/7mcPpAxCAYukzNwIQJZs/Q+MTIC+m32fTCfgyM9E2Heqciw=='))
    print(parasing_license(
        'a1OWOFsYZOmb9T/x/7A6NnnfeONNIe71a3+Ux+VFI4I4h6m82O5toEFf7doGd48Whjj2jLV/JVOnB/nAprjwiw=='))
