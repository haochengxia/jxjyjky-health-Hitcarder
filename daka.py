# coding=utf-8

"""jx jyjky daka script"""


import requests, json, os, logging, urllib3, time, random
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler


class Daka():
    def __init__(self, login_name, password, temperature=36.4) -> None:
        """init info"""
        
        self.login_name = login_name
        self.password = password
        
        self.temperature = str(round(temperature, 1))
        
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
            'ticket' : ''
        }
        
        self.login_url = 'https://jk.zjjxedu.gov.cn/sso/mobi/WxLogin2'
        self.post_url = 'https://jk.zjjxedu.gov.cn/health/mobiapi/savePunchclock'
        
        self.sess = requests.Session()

    def login(self):
        """Login to platform"""

        data = {
            'loginname': self.login_name,
            'password': self.password,
        }
        
        res = self.sess.post(url=self.login_url, data=data, verify = False)
        res = json.loads(res.content.decode())
        if res['code'] != 0:
            raise LoginError('[*] %s 登录失败，请核实账号密码重新登录，当前用户名%s' 
                             %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                             self.login_name))
        self.headers['ticket'] = res['data']['ticket']
        
        return self.sess
    
    def post(self):
        """Post the hitcard info"""
        
        self.info = {
            'temperature': self.temperature,
            'is_whether' : '1',
            'amorpm' : '0',
            'symptom' : '',
            'remark': '',
            'is_famwhether':'1',
            'famremark':'',
        }
        
        res = self.sess.post(self.post_url, data=self.info, headers=self.headers)
        return json.loads(res.text)

# Exceptions 
class LoginError(Exception):
    """Login Exception"""
    pass

def main(*temp_range):
    df = pd.read_csv('./list.csv')
    for item in df.values:
        for i in range(2):
            if not isinstance(item[i], str):
                item[i] = str(item[i])
        
        login_name = item[0]
        password = item[1]
        
        # 是否指定温度
        if len(item) > 2 and not pd.isnull(item[2]):
            dk = Daka(login_name, password, temperature=item[2])
        else:
            # 如不存在指定温度，配置文件是否生成随机温度
            if isinstance(temp_range[0], dict):
                dk = Daka(login_name, password, 
                         random.randrange(round(temp_range[0]["low_bound"] * 10), 
                                          round(temp_range[0]["high_bound"] * 10), 1) / 10)

            # 否则，使用默认温度
            else:
                dk = Daka(login_name, password)
            
        try:
            dk.login()
            res = dk.post()
            if res['code'] == 0:
                print('[+] %s 打卡成功，当前用户名%s \t打卡体温 %s' 
                      %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), dk.login_name, dk.temperature))
        except LoginError as err:
            print(err)


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    if os.path.exists('./config.json'):
        configs = json.loads(open('./config.json', 'r').read())
        hour = configs["schedule"]["hour"]
        minute = configs["schedule"]["minute"]
        # 是否指定随机温度
        flag_random = configs["temperature"]["random"]
        if flag_random:
            # 获取温度上下界
            temp_range = dict()
            temp_range["high_bound"] = configs["temperature"]["high_bound"]
            temp_range["low_bound"] = configs["temperature"]["low_bound"]
            
    main() if not 'temp_range' in vars() else main(temp_range)
    
    # Schedule task
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', args=[], hour=hour, minute=minute)
    print('已启动定时程序，每天 %02d:%02d 为您打卡' %(int(hour), int(minute)))
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass