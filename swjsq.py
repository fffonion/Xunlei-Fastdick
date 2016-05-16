#!/usr/bin/env python
from __future__ import print_function
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

rsa_mod = 0xAC69F5CCC8BDE47CD3D371603748378C9CFAD2938A6B021E0E191013975AD683F5CBF9ADE8BD7D46B4D2EC2D78AF146F1DD2D50DC51446BB8880B8CE88D476694DFC60594393BEEFAA16F5DBCEBE22F89D640F5336E42F587DC4AFEDEFEAC36CF007009CCCE5C1ACB4FF06FBA69802A8085C2C54BADD0597FC83E6870F1E36FD
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
        return "{0:0256X}".format(result) # length should be 1024bit, hard coded here
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

UNICODE_WARNING_SHOWN = False

header_xl = {
    'Content-Type':'',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'android-async-http/xl-acc-sdk/version-1.6.1.177600'
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


def long2hex(l):
    return hex(l)[2:].upper().rstrip('L')


def uprint(s, fallback = None, end = None):
    global UNICODE_WARNING_SHOWN
    while True:
        try:
            print(s, end = end)
        except UnicodeEncodeError:
            if UNICODE_WARNING_SHOWN:
                print('Warning: locale of your system may not be utf8 compatible, output will be truncated')
                UNICODE_WARNING_SHOWN = True
        else:
            break
        try:
            print(s.encode('utf-8'), end = end)
        except UnicodeEncodeError:
            if fallback:
                print(fallback, end = end)
        break

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
    fake_device_id = hashlib.md5("%s23333" % pwd_md5).hexdigest() # just generate a 32bit string
    # sign = div.10?.md5(sha1(packageName + businessType + md5(a protocolVersion specific GUID)))
    device_sign = "div100.%s%s" % (fake_device_id, hashlib.md5(hashlib.sha1("%scom.xunlei.vip.swjsq68700d1872b772946a6940e4b51827e8af" % fake_device_id).hexdigest()).hexdigest())
    _payload = json.dumps({
            "protocolVersion": 108,# 109
            "sequenceNo": 1000001, # TODO: autoincr when relogin
            "platformVersion": 1,
            "sdkVersion": 177550,# 177600
            "peerID": MAC,
            "businessType": 68,
            "clientVersion": "2.0.3.4",# app version
            "devicesign":device_sign,
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
                "e": "%06X" % rsa_pubexp,
                "n": long2hex(rsa_mod)
            },
            "extensionList": ""
    })
    ct = http_req('https://login.mobile.reg2t.sandai.net:443/', body = _payload, headers = header_xl, encoding = 'gbk')
    return json.loads(ct), _payload

def api_url():
    portal = json.loads(http_req("http://api.portal.swjsq.vip.xunlei.com:81/v2/queryportal"))
    if portal['errno']:
        print('Error: get interface_ip failed')
        os._exit(3)
    return '%s:%s' % (portal['interface_ip'], portal['interface_port'])

def setup():
    global MAC
    global API_URL
    MAC = get_mac(to_splt = '').upper() + '004V'
    API_URL = api_url()

def api(cmd, uid, session_id = ''):
    url = 'http://%s/v2/%s?peerid=%s&userid=%s&user_type=1%s' % (
            API_URL,
            cmd,
            MAC,
            uid,
            ('&sessionid=%s' % session_id) if session_id else ''
    )
    return json.loads(http_req(url, headers = header_api))

def fast_d1ck(uname, pwd, login_type, save = True):
    if uname[-2] == ':':
        print('Error: sub account can not upgrade')
        os._exit(3)

    dt, _payload = login_xunlei(uname, pwd, login_type)
    if 'sessionID' not in dt:
        uprint('Error: login failed, %s' % dt['errorDesc'], 'Error: login failed')
        print(dt)
        os._exit(1)
    elif ('isVip' not in dt or not dt['isVip']) and ('payId' not in dt or dt['payId'] not in  [5, 702]):
        #FIX ME: rewrite if with payId
        print('Warning: you are probably not xunlei vip, buy buy buy!\n[Debug] isVip:%s payId:%s payName:%s' % (
          'None' if 'isVip' not in dt else dt['isVip'],
          'None' if 'payId' not in dt else dt['payId'],
          'None' if 'payName' not in dt else [dt['payName']]
        ))
        #os._exit(2)
    print('Login xunlei succeeded')
    if save:
        try:
            os.remove(account_file_plain)
        except:
            pass
        with open(account_file_encrypted, 'w') as f:
            f.write('%s,%s' % (dt['userID'], pwd))
    _script_mtime = os.stat(os.path.realpath(__file__)).st_mtime
    if not os.path.exists(shell_file) or os.stat(shell_file).st_mtime < _script_mtime:
        make_wget_script(dt['userID'], pwd, _payload)
    if not os.path.exists(ipk_file) or os.stat(ipk_file).st_mtime < _script_mtime:
        update_ipk()

    _ = api('bandwidth', dt['userID'])
    if not _['can_upgrade']:
        uprint('Error: can not upgrade, so sad TAT %s' % _['message'], 'Error: can not upgrade, so sad TAT')
        os._exit(3)

    print("To Upgrade: ", end = '')
    uprint('%s%s ' % ( _['province_name'], _['sp_name']),
            '%s %s ' % ( _['province'], _['sp']),
            end = ''
          )
    print('Down %dM -> %dM, Up %dM -> %dM' % (
            _['bandwidth']['downstream']/1024,
            _['max_bandwidth']['downstream']/1024,
            _['bandwidth']['upstream']/1024,
            _['max_bandwidth']['upstream']/1024,
    ))

    #print(_)
    def _atexit_func():
        print("Sending recover request")
        try:
            api('recover', dt['userID'], dt['sessionID'])
        except KeyboardInterrupt:
            print('Secondary ctrl+c pressed, exiting')
    atexit.register(_atexit_func)
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
                if _['errno'] == 513:# TEST: re-upgrade when get 'not exist channel'
                    i = 0
                    continue
                else:
                    time.sleep(300)#os._exit(4)
        except Exception as ex:
            import traceback
            _ = traceback.format_exc()
            print(_)
        with open('swjsq.log', 'a') as f:
            try:
                f.write('%s %s\n' % (time.strftime('%X', time.localtime(time.time())), _))
            except UnicodeEncodeError:
                f.write('%s keepalive\n' % (time.strftime('%X', time.localtime(time.time()))))
        i+=1
        time.sleep(270)#5 min

def make_wget_script(uid, pwd, _payload):
    open(shell_file, 'wb').write(
'''#!/bin/ash
TEST_URL="https://baidu.com"
UA_XL="User-Agent: swjsq/0.0.1"

if [ ! -z "`wget --no-check-certificate -O - $TEST_URL 2>&1|grep "100%"`" ]
   then
   HTTP_REQ="wget -q --no-check-certificate -O - "
   POST_ARG="--post-data="
else
   command -v curl >/dev/null 2>&1 && curl -kI $TEST_URL >/dev/null 2>&1 || { echo >&2 "Xunlei-FastD1ck cannot find wget or curl installed with https(ssl) enabled in this system."; exit 1; }
   HTTP_REQ="curl -ks"
   POST_ARG="--data "
fi

uid='''+str(uid)+'''
pwd='''+rsa_encode(pwd)+'''
nic=eth0
peerid='''+MAC+'''
uid_orig=$uid

day_of_month_orig=`date +%d`
orig_day_of_month=`echo $day_of_month_orig|grep -oE "[1-9]{1,2}"`
portal=`$HTTP_REQ http://api.portal.swjsq.vip.xunlei.com:81/v2/queryportal`
portal_ip=`echo $portal|grep -oE '([0-9]{1,3}[\.]){3}[0-9]{1,3}'`
portal_port_temp=`echo $portal|grep -oE "port...[0-9]{1,5}"`
portal_port=`echo $portal_port_temp|grep -oE '[0-9]{1,5}'`
if [ -z "$portal_ip" ]
  then
	 sleep 30
	 portal=`$HTTP_REQ http://api.portal.swjsq.vip.xunlei.com:81/v2/queryportal`
     portal_ip=`echo $portal|grep -oE '([0-9]{1,3}[\.]){3}[0-9]{1,3}'`
     portal_port_temp=`echo $portal|grep -oE "port...[0-9]{1,5}"`
     portal_port=`echo $portal_port_temp|grep -oE '[0-9]{1,5}'`
	 if [ -z "$portal_ip" ]
          then
             portal_ip="119.147.41.210"
	         portal_port=80
	 fi
fi
api_url="http://$portal_ip:$portal_port/v2"
i=6
while true
do
    if test $i -ge 6
    then
        ret=`$HTTP_REQ https://login.mobile.reg2t.sandai.net:443/ $POST_ARG"'''+_payload.replace('"','\\"')+'''" --header $UA_XL`
        session_temp=`echo $ret|grep -oE "sessionID...[A-F,0-9]{32}"`
	 session=`echo $session_temp|grep -oE "[A-F,0-9]{32}"`
        uid_temp=`echo $ret|grep -oE "userID..[0-9]{9}"`
	 uid=`echo $uid_temp|grep -oE "[0-9]{9}"`
        i=0
	  if [ -z "$session" ]
        then
              echo "session is empty"
              i=6
              sleep 30
              uid=$uid_orig
              continue
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
        $HTTP_REQ "$api_url/upgrade?peerid=$peerid&userid=$uid&user_type=1&sessionid=$session"

    fi
    sleep 1
	day_of_month_orig=`date +%d`
    day_of_month=`echo $day_of_month_orig|grep -oE "[1-9]{1,2}"`
    if [[ -z $orig_day_of_month || $day_of_month -ne $orig_day_of_month ]]
     then
       orig_day_of_month=$day_of_month
       $HTTP_REQ "$api_url/recover?peerid=$peerid&userid=$uid&user_type=1&sessionid=$session"
       sleep 5
	fi
    ret=`$HTTP_REQ "$api_url/keepalive?peerid=$peerid&userid=$uid&user_type=1&sessionid=$session"`
    if [ ! -z "`echo $ret|grep "not exist channel"`" ]
    then
        i=6
    else
        let i=i+1
        sleep 270
    fi
done


'''.replace("\r", ""))

def update_ipk():
    def _sio(s = None):
        if not s:
            return sio()
        if PY3K:
            return sio(bytes(s, "ascii"))
        else:
            return sio(s)

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
    data_content = open(shell_file, 'rb')
    add_to_tar(data_fobj, './bin/swjsq', data_content)
    data_fobj.close()
    add_to_tar(ipk_fobj, './data.tar.gz', data_stream)
    data_stream.close()


    control_stream = sio()
    control_fobj = tarfile.open(fileobj = control_stream, mode = 'w:gz')
    control_content = _sio('''Package: swjsq
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

    debian_binary_stream = _sio('2.0\n')
    add_to_tar(ipk_fobj, './debian-binary', debian_binary_stream)
    debian_binary_stream.close()

    ipk_fobj.close()


if __name__ == '__main__':
    setup()
    try:
        if os.path.exists(account_file_plain):
            uid, pwd = open(account_file_plain).read().strip().split(',')
            if PY3K:
                pwd = pwd.encode('utf-8')
            fast_d1ck(uid, hashlib.md5(pwd).hexdigest(), TYPE_NORMAL_ACCOUNT)
        elif os.path.exists(account_file_encrypted):
            uid, pwd_md5 = open(account_file_encrypted).read().strip().split(',')
            fast_d1ck(uid, pwd_md5, TYPE_NUM_ACCOUNT, save = False)
        elif 'XUNLEI_UID' in os.environ and 'XUNLEI_PASSWD' in os.environ:
            uid = os.environ['XUNLEI_UID']
            pwd = os.environ['XUNLEI_PASSWD']
            fast_d1ck(uid, hashlib.md5(pwd).hexdigest(), TYPE_NORMAL_ACCOUNT)
        else:
            print('Please use XUNLEI_UID=<uid>/XUNLEI_PASSWD=<pass> envrionment varibles or create config file "%s", input account splitting with comma(,). Eg:\nyonghuming,mima' % account_file_plain)
    except KeyboardInterrupt:
        pass
