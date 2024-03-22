import subprocess
import os
import signal
from src.utils.config import CONF
from src.utils.singleton import singleton

@singleton
class WebSockifyManager:
    
    def __init__(self) -> None:
        self.process = None
        self.target_config_path = CONF["vnc"]["token_config"]
        self.websockfy_port = CONF["vnc"]['websockify_port']
        
    # 启动websockify子进程
    def start_websockify(self):
        # 构建启动WebSockify的命令
        command = ['websockify', str(self.websockfy_port), f'--target-config={self.target_config_path}']
        self.process = subprocess.Popen(command)
        return self.process

    #终止websockify
    def stop_websockify(self):
        # 终止WebSockify进程
        os.kill(self.process.pid, signal.SIGTERM)
    
    #修改配置文件
    def update_web_sockify_conf(self, key:str, value:str):
        file_path = self.target_config_path
        config = self._read_conf_file(file_path)
        config[key] = value
        self._write_conf_file(file_path, config)
        
    #删除配置项
    def delete_web_sockify_conf(self, key:str):
        file_path = self.target_config_path
        config = self._read_conf_file(file_path)
        if config[key]:
            del config[key]
            self._write_conf_file(file_path, config)
    
    
    def _read_conf_file(self, file_path) -> dict:
        config = {}
        with open(file_path, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    config[key.strip()] = value.strip()
        return config


    def _write_conf_file(self, file_path, config):
        with open(file_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}: {value}\n")

