#!/bin/bash

# 默认值
user_id=''
user_pwd=''
other_key=''
is_logout=0
urlA='wifi.cnu.edu.cn' # 对应 IP 地址 192.168.1.91
urlB='10.10.10.9'
cnu_url_1='http://wifi.cnu.edu.cn:801/'
cnu_url_2='https://wifi.cnu.edu.cn:802/'
logout_path='/drcom/logout?callback=dr1005'
login_path='/drcom/login?callback=dr1004'

function drcom_api_get(){
# 设置请求头和请求体
    url_header=$1
    path=$2
    data=$3

    url="http://${url_header}${path}${data}"
    headers="Host: ${url_header}
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0
    Accept: */*
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: ${url_header}/a79.htm"
    # 发送 HTTP GET 请求
    curl -s -X GET -H "$headers" -d "" "$url"
}

function conn_check(){
  # 获取网络接口名称
  interface=$(ip route | awk '/default/ {print $5}')
  is_wl=0
  # 判断是否为无线接口
  if [[ $interface == *"wlan"* || $interface == *"wl"* ]]; then
      echo "Wireless connection detected on interface: $interface"
      is_wl=1
  elif [[ $interface == *"eth"* || $interface == *"enp"* || $interface == *"eno"* ]]; then
      echo "Wired connection detected on interface: $interface"
      is_wl=0
  else
      echo "Unknown connection type on interface: $interface"
      is_wl=-1
  fi
}
function result_error(){
    if [ -z "$result" ]; then
        echo "ERROR! Failed to retrieve result value. "
        echo "Help Doc"
        echo "A. Check the status of your network"
        echo "B. Try again in 40 seconds"
        exit -1
    fi
}
function usage() { echo "Usage: $0 [-e] [-u user_account] [-p password] 
-e is logout account,
Logout Example: $0 -e
Login Example: $0 -u 65123 -p mypassword1" 1>&2; exit 1; }



# 解析输入参数
while getopts "u:p:e" opt; do
  case $opt in
    u)
      user_id=$OPTARG
      ;;
    p)
      user_pwd=$OPTARG
      ;;
    e)
      is_logout=1
      ;;
    \?)
      usage
      ;;
  esac
done

logout_data="&jsVersion=4.2.1&v=9193&lang=zh"

conn_check

if [ $is_wl -eq 1 ]; then
  url=$urlA
elif [ $is_wl -eq 0 ]; then
  url=$urlB
elif [ $is_wl -eq -1 ]; then
  url=$urlB
else
  echo "Unknown connection type, cannot proceed."
  exit 1
fi

if [ $is_logout -eq 1 ];then
    ret_json=$(drcom_api_get $url $logout_path $logout_data)
    result=$(echo "$ret_json" | sed 's/.*"result":\([^,}]*\).*/\1/')
    msga=$(echo "$ret_json" | awk -F'"msga":"' '{print $2}' | awk -F'"' '{print $1}')
    # echo "result: $result"
    result_error
    if [ $result -eq 1 ];then
        echo "msga: $msga Logout Success!"
        echo "The device doesn't seem to be a login to the network."
    else
        echo "msga: $msga"
    fi
    exit 0
fi

# 检查是否提供了必要的用户认证信息
if [ -z "$user_id" ] || [ -z "$user_pwd" ]; then
  echo "Please provide both user ID (-u) and password (-p)."
  exit 1
fi

login_data="&DDDDD=%2C%60%2C${user_id}&upass=${user_pwd}&0MKKey=123456&R1=0&R2=&R3=0&R6=0&para=00&v6ip=&R7=1&terminal_type=1&lang=zh-cn&jsVersion=4.2.1&v=973&lang=zh"

ret_json=$(drcom_api_get $url $login_path $login_data)
result=$(echo "$ret_json" | sed 's/.*"result":\([^,}]*\).*/\1/')
msga=$(echo "$ret_json" | awk -F'"msga":"' '{print $2}' | awk -F'"' '{print $1}')

result_error

if [ $result -eq 1 ];then
    echo "msga: $msga Login Success!"
else
    echo "msga: $msga"
    exit -1
fi
# Error code: 205 Auth Error(-199) 
exit 0
