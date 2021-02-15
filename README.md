# JX jyjky 自动打卡脚本

项目用于学习交流

## Usage
1. clone 本项目并进入目录
    ```bash
    $ git clone https://github.com/haochengxia/jxjyjky-health-Hitcarder.git --depth 1

    $ cd jxjyjky-health-Hitcarde
    ```

2. 安装依赖
   ```bash
   $ pip3 install -r requirements.txt
   ```

3. 创建/修改配置文件和填写打卡人员信息，涉及文件`list.csv`和`config.json`。

    a. 文件list.csv中的内容为打卡人员信息：

    ```python
    ID,password,temperature
    [用户1身份证号],hy123456,<上报体温(可选)>
    [用户2身份证号],hy123456,<上报体温(可选)>
    ...
    ```

    提示: 登陆默认密码为hy123456，如果修改了可直接在csv文件中进行改动。

    b. config.json中的内容为自动打卡定时信息(默认7点15分打卡)：
    ```json
    {
        "schedule":
        {
        "hour": 7,
        "minute": 15
        }
    }
    ```
4. 启动定时打卡脚本
   ```bash
   $ python3 daka.py
   ```
   > 后台运行可使用tmux或nohup等，如nohup python3 daka.py &


