# 部署说明：在 Linux 服务器上静默运行 Python 机器人

## 一. 环境准备

1. **安装 Python 3**
   确保你的服务器上安装了 Python 3.x。可以通过以下命令检查：
   ```bash
   python3 --version
   ```

2. **安装所需库**
   安装项目所需的 Python 包，使用以下命令：
   ```bash
   pip install -r requirements.txt
   ```
   确保你的 `requirements.txt` 文件中包含了 `aiohttp`、`psutil` 和 `qqbot` 等必需库。

## 二. 代码部署

1. **上传代码**
   将 `robot.py` 和 `config.yaml` 文件上传到你的 Linux 服务器中，通常位置可以放在 `/home/user/QQbot/` 目录下。

2. **权限设置**
   为 `robot.py` 文件添加可执行权限，运行：
   ```bash
   chmod +x robot.py
   ```

## 三. 静默运行

### 1. 使用 `nohup` 命令

可以使用 `nohup` 命令将 Python 脚本放在后台运行，即使关闭终端也会继续运行。

打开终端，进入程序目录，然后执行以下命令：
```bash
nohup python3 robot.py > robot.log 2>&1 &
```

- `nohup`：不挂断运行，即使退出终端也不会停止程序。
- `python3 robot.py`：执行你的 Python 脚本。
- `> robot.log`：将标准输出重定向到 `robot.log` 文件中。
- `2>&1`：将错误输出也重定向到 `robot.log` 文件中。
- `&`：将程序放入后台运行。

### 2. 使用 Systemd 管理服务（可选）

对于较复杂的部署，可以考虑使用 Systemd 管理脚本。创建一个 Systemd 服务文件，例如 `/etc/systemd/system/qqbot.service`，内容如下：

```ini
[Unit]
Description=QQ Bot Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/QQbot/robot.py
WorkingDirectory=/home/QQbot
StandardOutput=append:/home/QQbot/robot.log
StandardError=append:/home/QQbot/robot.log
Restart=always

[Install]
WantedBy=multi-user.target
```

保存后，使用以下命令启动和启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start qqbot.service
sudo systemctl enable qqbot.service
```

## 四. 查看日志内容

1. **查看实时日志**
   可以使用 `tail` 命令查看 `output.log` 文件，获取实时日志输出：
   ```bash
   tail -f output.log
   ```

2. **查看历史日志**
   使用 `cat` 命令查看全部日志：
   ```bash
   cat output.log
   ```

3. **使用 `less` 查看**
   命令也可以使用 `less` 进行简单的分页查看，非常方便：
   ```bash
   less output.log
   ```

## 五. 停止运行

如果需要停止后台运行的进程，可以使用以下命令查找进程 ID（PID）并 kill 进程：
```bash
ps aux | grep robot.py
```
找到对应的 PID 后，使用命令：
```bash
kill <PID>
```

如果使用 Systemd 管理，可以使用：
```bash
sudo systemctl stop qqbot.service
```

## 总结

通过上述步骤，你可以在 Linux 服务器上成功部署你的 Python 机器人程序，使其静默运行并能够方便地查看日志内容。确保定期检查日志文件以监控机器人的运行状态和性能。