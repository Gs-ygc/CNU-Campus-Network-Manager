#!/usr/bin/python3

from time import sleep
import requests
import sys
import getopt
from bs4 import BeautifulSoup
import warnings
import logging
import json

class TextStyle:
    HEADER = '\033[1;33m'  # 加粗黄色
    GREEN = '\033[1;32m'   # 加粗绿色
    END = '\033[0m'        # 恢复默认样式

# var epHTTPPort=801; // eportal http 端口        
# var enHTTPSPort=802; // eportal https 端口

class CnuNet :

    logging_level = logging.NOTSET
    __username = "your_username"
    __password = "your_password"
    __debug = False
    __base_url = "http://wifi.cnu.edu.cn"
    __response=None
    __response_ditc = {}
    __post_data = None
    __info_port = "801"
    __info_base_url = __base_url+":"+__info_port+"/eportal/portal/custom/"
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    login_post_data = {
        "DDDDD": None,
        "upass": None,
        "0MKKey": ""# 123456
    }

    ipMsg_url = __info_base_url + "loadOnlineDevice"
    userInfo_url = __info_base_url + "loadUserInfo"

    ipMsg_response_json = None
    ipMsg_post_data = {
        "callback": "dr1003",
        "account": "null",
        "wlan_user_ip": None,
        'is_login': '1'
    }

    userInfo_response_json = None
    userInfo_post_data = {
        'callback': 'dr1002',
        'account': 'null',
        'wlan_user_ip': None,
    }

    def __init__(self, username, password, debug):
        self.session = requests.session()
        self.__username = username
        self.__password = password
        self.debug = debug
        self.__post_data=self.login_post_data
        self.__post_data.update({"DDDDD": username,"upass": password,})

        if debug :
            self.logging_level=logging.DEBUG
            logging.basicConfig(level=self.logging_level,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        if self.debug:
            if self.test_net_init():
                self.update_response_ditc()
                my_ip = self.__response_ditc.get('v46ip', 'Not found')
                ser_ip= self.__response_ditc.get('v4serip', 'Not found')
                my_mac= self.__response_ditc.get('ss4', 'Not found').upper()
                print(my_ip)
                print(ser_ip)
                print(my_mac)

    def check_online(self):
        response=self.session.get('http://wifi.cnu.edu.cn:801/eportal/portal/online_list',headers=self.__headers)
        self.online_json=json.loads(response.text[response.text.index('(') + 1: -2])
        return bool(self.online_json["result"])
    
    def print_online_info(self):
        print(f"{TextStyle.HEADER}Current Login Information{TextStyle.END}")
        data = self.online_json['list']
        for i in range(int(self.online_json["total"])):
            online_time = str(data[i]['online_time'])
            used_time = str(int(data[i]['time_long'])//60)
            online_ip = str(data[i]['online_ip'])
            uplink_Mbytes = str(int(data[i]['uplink_bytes'])//1000)
            downlink_Mbytes = str(int(data[i]['downlink_bytes'])//1000)
            dhcp_host = str(data[i]['dhcp_host'])
            mac_address = str(data[i]['online_mac'])
            user_account = str(data[i]['user_account'])

            print('{:<12} {:<15} {:<10} {:<10} {:<10} {:<15} {:<15} {:<25}'.format('Host Name', 'User Account', 'OnlineT', 'Upload','Download', 'Online Ip', 'MAC Address', 'Last login on the device'))
            print('{:<12} {:<15} {:<10} {:<10} {:<10} {:<15} {:<15} {:<25}'.format(dhcp_host, user_account, used_time+'Min', uplink_Mbytes +'MB', downlink_Mbytes + 'MB', online_ip, mac_address, online_time))
    
    def get_post_data(self):
        if self.__debug:
            print(self.__post_data)
        return self.__post_data
    
    def test_net_init(self):
        Access = False
        try:
            self.__response = self.session.get(self.__base_url, headers=self.__headers)
            if self.debug:
                print(self.__response.text)
            Access = True
        except self.session.exceptions.ConnectionError:
            warnings.warn('ConnectionError! ', RuntimeWarning)
            print('\033[31m' + 'No address associated with hostname' + '\033[0m')
        except self.session.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError')
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
        
        return Access

    def update_response_ditc(self):
        soup = BeautifulSoup(self.__response.text, 'html.parser')

        # 查找并打印关键输出

        script_tag = soup.find('script')
        if script_tag:
            output = script_tag.text
        else:
            logging.warning("script error!")

        output_lines = []
        for line in output.split('\n'):
            line = line.split('//')[0].strip()
            if line:
                output_lines.append(line)

        output_cleaned = '\n'.join(output_lines)

        # 将提取的内容存储到字典中
        self.__response_ditc = {}
        for line in output_cleaned.split(';'):
            if '=' in line:
                key_value = line.split('=')
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    self.__response_ditc[key] = value 

    def post(self, url, data):
        Accessed = False
        try:
            self.__response = self.session.post(url,data=data,headers=self.__headers)
            logging.info(self.__response.text)
            Accessed = True
        except self.session.exceptions.ConnectionError:
            print('\033[31m' + 'No address associated with hostname' + '\033[0m')
        except self.session.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError')
        except:
            print('Unfortunitely -- An Unknow Error Happened')

        if Accessed == False:
            print("CNU Net ERROR")
            logging.error("CNU Net ERROR")
        
        return Accessed

    def login(self):
        Accessed = False
        try:
            self.__response = self.session.post(self.__base_url,data=self.__post_data,headers=self.__headers)
            Accessed = True
        except self.session.exceptions.ConnectionError:
            print('\033[31m' + 'No address associated with hostname' + '\033[0m')
        except self.session.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError')
        except:
            print('Unfortunitely -- An Unknow Error Happened')

        if Accessed == False:
            print("CNU Net ERROR")
            logging.error("CNU Net ERROR")
            return Accessed
        
        if self.__debug :
            print(self.__response.text)

        self.update_response_ditc()

        login_msg = self.__response_ditc.get('msga', 'Not found')
        if login_msg != 'Not found':
            logging.error("login error "+login_msg)
        else:
            logging.info("user"+"login success!")
            logging.info("uid:"+self.__response_ditc.get('UID', 'Not found'))
            return True

    def logout(self):
        print() # TODO logout

    def update_login_usr_info(self):
        self.post(self.ipMsg_url, self.ipMsg_post_data)
        self.ipMsg_response_json = json.loads(\
            self.__response.text\
                [self.__response.text.index('(') + 1: -2])

        self.post(self.userInfo_url,self.userInfo_post_data)
        self.userInfo_response_json = json.loads(\
            self.__response.text\
                [self.__response.text.index('(') + 1: -2])
        
    def print_login_usr_info(self):
        userInfo_len = len(self.userInfo_response_json['data'])
        if userInfo_len==0:
            logging.error("userInfo_len == 0")
            return
        data = self.userInfo_response_json['data']
        used_time = str(data[0]['USERTIME'])
        used_data = str(data[0]['USERFLOW'])
        account_balance = str(data[0]['USERMONEY'])
        mac_address = str(data[0]['MAC'])

        print(f"{TextStyle.HEADER}Current Account Information{TextStyle.END}")

        print('{:<12} {:<15} {:<10} {:<15}'.format('Used Time', 'Used Data','Balance', 'MAC Address'))
        print('{:<12} {:<15} {:<10} {:<15}'.format(used_time+"Min", used_data+"MB", account_balance+" RMB", mac_address))

        ipMsg_len = len(self.ipMsg_response_json['data'])
        if userInfo_len==0:
            logging.error("userInfo_len == 0")
            return
        data = self.ipMsg_response_json['data']
        print(f"{TextStyle.HEADER}Login Devices {TextStyle.END}")
        print('{:<12} {:<25} {:<15} {:<15}'.format('Number', 'Online Time', 'Login IP','MAC Address'))
        for i in range(ipMsg_len):
            print('{:<12} {:<25} {:<15} {:<15}'.format(data[i]['session_id'], data[i]['login_time'], data[i]['login_ip'], data[i]['mac_address']))


    def print_response_ditc(self):
        for key,value in self.__response_ditc.items():
            print(key+": "+str(value))
        


def param_parser(argv):
    # --help -help
    # --usrname= -u
    # --password= -p
    # --debug -d
    global my_username
    global my_password
    global debug

    try:
        opts, args = getopt.getopt(argv, "hu:p:d", ["username=", "password=", "debug"])
    except getopt.GetoptError:
        print('Usage: CnuNet.py -u <username> -p <password> [-d]')
        sys.exit(2)
    opt_flag=0
    for opt, arg in opts:
        if opt in ("-u", "--username"):
            my_username = arg
            opt_flag|=0x1
        elif opt in ("-p", "--password"):
            my_password = arg
            opt_flag|=0x10
        elif opt in ("-d", "--debug"):
            debug = True
    if opt_flag!=0x11 :
        print('Usage: CnuNet.py -u <username> -p <password> [-d]')
        sys.exit(2)
    if debug:
        print('Username:', my_username)
        print('Password:', my_password)
        print('Debug mode:', debug)


if __name__ == "__main__":
    my_username = ''
    my_password = ''
    debug = False
    param_parser(sys.argv[1:])
    
    cnu_net = CnuNet(username=my_username,
                     password=my_password,
                     debug=debug)
    if cnu_net.check_online()==0:
        logging.error(cnu_net.online_json["msg"])
        if cnu_net.login() :
            print("Login is success")
            exit(0)
        else :
            print("Login is error")
            exit(-1)
    
    sleep(2)
    cnu_net.print_online_info()
    cnu_net.update_login_usr_info()
    cnu_net.print_login_usr_info()

    exit(-1)


    
	
