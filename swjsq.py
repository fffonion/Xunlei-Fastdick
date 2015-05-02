
import os
import re
import sys
import json
import time
import hashlib
import binascii
import ssl

#xunlei use self-signed certificate; on py2.7.9+
if hasattr(ssl, '_create_unverified_context') and hasattr(ssl, '_create_default_https_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

rsa_mod = 0xD6F1CFBF4D9F70710527E1B1911635460B1FF9AB7C202294D04A6F135A906E90E2398123C234340A3CEA0E5EFDCB4BCF7C613A5A52B96F59871D8AB9D240ABD4481CCFD758EC3F2FDD54A1D4D56BFFD5C4A95810A8CA25E87FDC752EFA047DF4710C7D67CA025A2DC3EA59B09A9F2E3A41D4A7EFBB31C738B35FFAAA5C6F4E6F
rsa_pubexp = 0x010001
if sys.version.startswith('2'):
    import urllib2
    rsa_pubexp = long(rsa_pubexp)
else:
    import urllib.request as urllib2

account_file_encrypted = '.swjsq.account'
account_file_plain = 'swjsq.account.txt'

try:
    from Crypto.PublicKey import RSA
except ImportError:
    #slow rsa
    print('Warning: pycrypto not found, use pure-python implemention')
    rsa_result = {}
    def cached(func):
        def _(s):
            if s in rsa_result:
                _r = rsa_result[s]
            else:
                _r = func(s)
                rsa_result[s] = _r
            return _r
        return _
    # https://github.com/mengskysama/XunLeiCrystalMinesMakeDie/blob/master/run.py
    def modpow(b, e, m):
        result = 1
        while (e > 0):
            if e & 1:
                result = (result * b) % m
            e = e >> 1
            b = (b * b) % m
        return result

    def str_to_int(string):
        str_int = 0
        for i in range(len(string)):
            str_int = str_int << 8
            str_int += ord(string[i])
        return str_int

    @cached
    def rsa_encode(data):
        result = modpow(str_to_int(data), long(rsa_pubexp, 16), long(rsa_mod, 16))
        return hex(result).upper()[2:-1].upper()
else:
    cipher = RSA.construct((rsa_mod, rsa_pubexp))
    def rsa_encode(s):
        return binascii.hexlify(cipher.encrypt(s, None)[0]).upper()


TYPE_NORMAL_ACCOUNT = 0
TYPE_NUM_ACCOUNT = 1

header_xl = {
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'android-async-http/1.4.3 (http://loopj.com/android-async-http)'
}
header_api = {
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.0.1; SmallRice Build/LRX22C)'
}

def get_mac(nic = '', to_splt = ':'):
    if os.name == 'nt':
        cmd = 'ipconfig /all'
        splt = '-'
    elif os.name == "posix":
        cmd = 'ifconfig %s' % (nic or '-a')
        splt = ':'
    else:
        return ''
    try:
        r = os.popen(cmd).read()
        if r:
            _ = re.findall('((?:[0-9A-Fa-f]{2}%s){5}[0-9A-Fa-f]{2})' % splt, r)
            if not _:
                return ''
            else:
                return _[0].replace(splt, to_splt)
    except:
        pass
    return ret

MAC = get_mac(to_splt = '').upper() + '004V'


def long2hex(l):
    return hex(l)[2:].upper().rstrip('L')

def http_req(url, headers = {}, body = None):
    req = urllib2.Request(url)
    for k in headers:
        req.add_header(k, headers[k])
    resp = urllib2.urlopen(req, data = body)
    return resp.read()

def login_xunlei(uname, pwd_md5, login_type = TYPE_NORMAL_ACCOUNT):
    pwd = rsa_encode(pwd_md5)

    ct = http_req('https://login.mobile.reg2t.sandai.net:443/', body = json.dumps(
        {
            "protocolVersion": 101,
            "sequenceNo": 1000001,
            "platformVersion": 1,
            "peerID": MAC,
            "businessType": 68,
            "clientVersion": "1.1",
            "isCompressed": 0,
            "cmdID": 1,
            "userName": uname,
            "passWord": pwd,
            "loginType": login_type,
            "sessionID": "",
            "verifyKey": "",
            "verifyCode": "",
            "appName": "ANDROID-com.xunlei.vip.swjsq",
            "rsaKey": {
                "e": long2hex(rsa_pubexp),
                "n": long2hex(rsa_mod)
            },
            "extensionList": ""
        }), headers = header_xl
    )
    return json.loads(ct.decode('gbk'))


def api(cmd, uid, session_id = ''):
    url = 'http://api.swjsq.vip.xunlei.com/v2/%s?peerid=%s&userid=%s&user_type=1%s' % (
            cmd,
            MAC,
            uid,
            ('sessionid=%s' % session_id) if session_id else ''
    )
    return json.loads(http_req(url, headers = header_api))

def fast_d1ck(uname, pwd, login_type, save = True):
    if uname[-2] == ':':
        print('Error: sub account can not upgrade')
        os._exit(3)

    dt = login_xunlei(uname, pwd, login_type)
    if 'sessionID' not in dt:
        print('Error: login failed, %s' % dt['errorDesc'])
        os._exit(1)
    elif 'isVip' not in dt or not dt['isVip']:
        print('Error: you are not xunlei vip, buy buy buy! http://vip.xunlei.com/')
        os._exit(2)
    print('Login xunlei succeeded')
    if save:
        try:
            os.remove(account_file_plain)
        except:
            pass
        with open(account_file_encrypted, 'w') as f:
            f.write('%s,%s' % (dt['userID'], pwd))

    _ = api('bandwidth', dt['userID'])
    if not _['can_upgrade']:
        print('Error: can not upgrade, so sad TAT %s' % _['message'])
        os._exit(3)

    print('To Upgrade: %s%s Down %dM -> %dM, Up %dM -> %dM' % (
        _['province_name'], _['sp_name'],
        _['bandwidth']['downstream']/1024,
        _['max_bandwidth']['downstream']/1024,
        _['bandwidth']['upstream']/1024,
        _['max_bandwidth']['upstream']/1024,
    ))

    i = 0
    while True:
        try:
            if i == 0:#30min
                print('Initializing upgrade')
                _ = api('upgrade', dt['userID'], dt['sessionID'])
                if not _['errno']:
                    print('Upgrade done: Down %dM, Up %dM' % (_['bandwidth']['downstream'], _['bandwidth']['upstream']))
            else:
                _ = api('keepalive', dt['userID'], dt['sessionID'])
            if _['errno']:
                print('Error: %s' % _['message'])
                os._exit(4) 
        except Exception as ex:
            import traceback
            _ = traceback.format_exc()
            print(_)
        open('swjsq.log', 'a').write('%s %s\n' % (time.strftime('%X', time.localtime(time.time())), _))
        i+=1
        time.sleep(300)#5 min

if __name__ == '__main__':
    if os.path.exists(account_file_encrypted):
        uid, pwd_md5 = open(account_file_encrypted).read().strip().split(',')
        fast_d1ck(uid, pwd_md5, TYPE_NUM_ACCOUNT, save = False)
    elif os.path.exists(account_file_plain):
        uid, pwd = open(account_file_plain).read().strip().split(',')
        fast_d1ck(uid, hashlib.md5(pwd).hexdigest(), TYPE_NORMAL_ACCOUNT)
    else:
        print('Please create config file "%s", input account splitting with comma(,). Eg:\nyonghuming,mima' % account_file_plain)

    
    