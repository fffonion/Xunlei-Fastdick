
import os
import re
import sys
import json
import time
import hashlib
import binascii
import tarfile
import ssl
import atexit

#xunlei use self-signed certificate; on py2.7.9+
if hasattr(ssl, '_create_unverified_context') and hasattr(ssl, '_create_default_https_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

rsa_mod = 0xD6F1CFBF4D9F70710527E1B1911635460B1FF9AB7C202294D04A6F135A906E90E2398123C234340A3CEA0E5EFDCB4BCF7C613A5A52B96F59871D8AB9D240ABD4481CCFD758EC3F2FDD54A1D4D56BFFD5C4A95810A8CA25E87FDC752EFA047DF4710C7D67CA025A2DC3EA59B09A9F2E3A41D4A7EFBB31C738B35FFAAA5C6F4E6F
rsa_pubexp = 0x010001
PY3K = sys.version.startswith('3')
if not PY3K:
    import urllib2
    from cStringIO import StringIO as sio
    rsa_pubexp = long(rsa_pubexp)
else:
    import urllib.request as urllib2
    from io import BytesIO as sio

account_file_encrypted = '.swjsq.account'
account_file_plain = 'swjsq.account.txt'
shell_file = 'swjsq_wget.sh'
ipk_file = 'swjsq_0.0.1_all.ipk'

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
        result = modpow(str_to_int(data), rsa_pubexp, rsa_mod)
        return hex(result).upper()[2:].rstrip('L').upper()
else:
    cipher = RSA.construct((rsa_mod, rsa_pubexp))
    def rsa_encode(s):
        if PY3K and isinstance(s, str):
            s = s.encode("utf-8")
        _ = binascii.hexlify(cipher.encrypt(s, None)[0]).upper()
        if PY3K:
            _ = _.decode("utf-8")
        return _


TYPE_NORMAL_ACCOUNT = 0
TYPE_NUM_ACCOUNT = 1

header_xl = {
    'Content-Type':'',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'android-async-http/1.4.3 (http://loopj.com/android-async-http)'
}
header_api = {
    'Content-Type':'',
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
    return '000000000000004V'

MAC = get_mac(to_splt = '').upper() + '004V'


def long2hex(l):
    return hex(l)[2:].upper().rstrip('L')

def http_req(url, headers = {}, body = None, encoding = 'utf-8'):
    req = urllib2.Request(url)
    for k in headers:
        req.add_header(k, headers[k])
    if sys.version.startswith('3') and isinstance(body, str):
        body = bytes(body, encoding = 'ascii')
    resp = urllib2.urlopen(req, data = body)
    ret = resp.read().decode(encoding)
    if sys.version.startswith('3') and isinstance(ret, bytes):
        ret = str(ret)
    return ret

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
        }), headers = header_xl, encoding = 'gbk'
    )
    return json.loads(ct)

def api_url():
    portal = json.loads(http_req("http://api.portal.swjsq.vip.xunlei.com:81/v2/queryportal"))
    if portal['errno']:
        print('Error: get interface_ip failed')
        os._exit(3)
    return '%s:%s' % (portal['interface_ip'], portal['interface_port'])
API_URL = api_url()

def api(cmd, uid, session_id = ''):
    url = 'http://%s/v2/%s?peerid=%s&userid=%s&user_type=1%s' % (
            API_URL,
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
    if not os.path.exists(shell_file):
        make_wget_script(dt['userID'], pwd)
    if not os.path.exists(ipk_file):
        update_ipk()

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
    #print(_)
    atexit.register(lambda: api('recover', dt['userID'], dt['sessionID']))
    i = 0
    while True:
        try:
            if i % 6 == 0:#30min
                print('Initializing upgrade')
                if i:
                    api('recover', dt['userID'], dt['sessionID'])
                    time.sleep(5)
                    dt = login_xunlei(uname, pwd, login_type)
                _ = api('upgrade', dt['userID'], dt['sessionID'])
                #print(_)
                if not _['errno']:
                    print('Upgrade done: Down %dM, Up %dM' % (_['bandwidth']['downstream'], _['bandwidth']['upstream']))
            else:
                _ = api('keepalive', dt['userID'], dt['sessionID'])
            if _['errno']:
                print('Error: %s' % _['message'])
                time.sleep(300)#os._exit(4) 
        except Exception as ex:
            import traceback
            _ = traceback.format_exc()
            print(_)
        open('swjsq.log', 'a').write('%s %s\n' % (time.strftime('%X', time.localtime(time.time())), _))
        i+=1
        time.sleep(270)#5 min

def make_wget_script(uid, pwd):
    open(shell_file, 'w').write(
'''#!/bin/ash
uid='''+str(uid)+'''
pwd='''+rsa_encode(pwd)+'''
nic=eth0
peerid='''+MAC+'''
uid_orig=$uid

portal=`curl http://api.portal.swjsq.vip.xunlei.com:81/v2/queryportal`
portal_ip=`echo $portal|grep -oE '([0-9]{1,3}[\.]){3}[0-9]{1,3}'`
portal_port_temp=`echo $portal|grep -oE "port...[0-9]{1,5}"`
portal_port=`echo $portal_port_temp|grep -oE '[0-9]{1,5}'`
api_url="http://$portal_ip:$portal_port/v2"
if [ -z "$portal_ip" ]
  then
	 sleep 30
	 portal=`curl http://api.portal.swjsq.vip.xunlei.com:81/v2/queryportal`
     portal_ip=`echo $portal|grep -oE '([0-9]{1,3}[\.]){3}[0-9]{1,3}'`
     portal_port_temp=`echo $portal|grep -oE "port...[0-9]{1,5}"`
     portal_port=`echo $portal_port_temp|grep -oE '[0-9]{1,5}'`
	 if [ -z "$portal_ip" ]
          then
             portal_ip="119.147.41.210"
	         portal_port=80
	 fi
fi
i=6
while true
do
    if test $i -ge 6
    then
        ret=`curl -k --data "{\\"userName\\": \\""$uid"\\", \\"businessType\\": 68, \\"clientVersion\\": \\"1.1\\", \\"appName\\": \\"ANDROID-com.xunlei.vip.swjsq\\", \\"isCompressed\\": 0, \\"sequenceNo\\": 1000001, \\"sessionID\\": \\"\\", \\"loginType\\": 1, \\"rsaKey\\": {\\"e\\": \\"'''+long2hex(rsa_pubexp)+'''\\", \\"n\\": \\"'''+long2hex(rsa_mod)+'''\\"}, \\"cmdID\\": 1, \\"verifyCode\\": \\"\\", \\"peerID\\": \\""$peerid"\\", \\"protocolVersion\\": 101, \\"platformVersion\\": 1, \\"passWord\\": \\""$pwd"\\", \\"extensionList\\": \\"\\", \\"verifyKey\\": \\"\\"}" https://login.mobile.reg2t.sandai.net:443/`
        session_temp=`echo $ret|grep -oE "sessionID...[A-F,0-9]{32}"`
	 session=`echo $session_temp|grep -oE "[A-F,0-9]{32}"`
        uid_temp=`echo $ret|grep -oE "userID..[0-9]{9}"`
	 uid=`echo $uid_temp|grep -oE "[0-9]{9}"`
        i=0
	  if [ -z "$session" ]
        then
              echo "session is empty"
	       i=5
        else
              echo "session is $session"
        fi

      if [ -z "$uid" ]
        then
	        echo "uid is empty"
			uid=$uid_orig
        else
            echo "uid is $uid"			
        fi
        curl "$api_url/upgrade?peerid=$peerid&userid=$uid&user_type=1&sessionid=$session"		
    fi
    sleep 1
    curl "$api_url/keepalive?peerid=$peerid&userid=$uid&user_type=1&sessionid=$session"
    let i=i+1
    sleep 270
done


''')

def update_ipk():
    #FIXME: 3.X compatibility
    def get_sio(tar, name):
        return sio(tar.extractfile(name).read())

    def flen(fobj):
        pos = fobj.tell()
        fobj.seek(0)
        _ = len(fobj.read())
        fobj.seek(pos)
        return _

    def add_to_tar(tar, name, sio_obj, mode = 33279):
        info = tarfile.TarInfo(name = name)
        info.size = flen(sio_obj)
        info.mode = mode
        sio_obj.seek(0)
        tar.addfile(info, sio_obj)


    if os.path.exists(ipk_file):
        os.remove(ipk_file)
    ipk_fobj = tarfile.open(name = ipk_file, mode = 'w:gz')

    data_stream = sio()
    data_fobj = tarfile.open(fileobj = data_stream, mode = 'w:gz')
    data_content = open(shell_file, 'r')
    add_to_tar(data_fobj, './bin/swjsq', data_content)
    data_fobj.close()
    add_to_tar(ipk_fobj, './data.tar.gz', data_stream)
    data_stream.close()


    control_stream = sio()
    control_fobj = tarfile.open(fileobj = control_stream, mode = 'w:gz')
    control_content = sio('''Package: swjsq
Version: 0.0.1
Depends: libc
Source: none
Section: net
Maintainer: fffonion
Architecture: all
Installed-Size: %d
Description:  Xunlei Fast Dick
''' % flen(data_content))
    add_to_tar(control_fobj, './control', control_content)
    control_fobj.close()
    add_to_tar(ipk_fobj, './control.tar.gz', control_stream)
    control_stream.close()

    data_content.close()
    control_content.close()

    debian_binary_stream = sio('2.0\n')
    add_to_tar(ipk_fobj, './debian-binary', debian_binary_stream)
    debian_binary_stream.close()

    ipk_fobj.close()


if __name__ == '__main__':
    try:
        if os.path.exists(account_file_plain):
            uid, pwd = open(account_file_plain).read().strip().split(',')
            if PY3K:
                pwd = pwd.encode('utf-8')
            fast_d1ck(uid, hashlib.md5(pwd).hexdigest(), TYPE_NORMAL_ACCOUNT)
        elif os.path.exists(account_file_encrypted):
            uid, pwd_md5 = open(account_file_encrypted).read().strip().split(',')
            fast_d1ck(uid, pwd_md5, TYPE_NUM_ACCOUNT, save = False)
        else:
            print('Please create config file "%s", input account splitting with comma(,). Eg:\nyonghuming,mima' % account_file_plain)
    except KeyboardInterrupt:
        pass

    
    
