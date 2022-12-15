import psutil
import platform
import subprocess
import socket
import os
from datetime import datetime
import time

class Telemetry:
    def getProcess():
        pid = os.getpid()
        process = psutil.Process(pid)
        return process

    def getMachineInfo():
        system = platform.uname().system
        release = platform.uname().release
        machine = platform.uname().machine
        arch = platform.architecture()[0]
        kernel = platform.platform()
        return system,release,machine,arch,kernel

    def getBenchmarkInfo(process):
        cpu_percent = str(process.cpu_percent(interval=None))
        memory_percent = str(process.memory_percent(memtype="rss"))
        text_usage = str(process.memory_full_info().text/1024/1024)
        data_usage = str(process.memory_full_info().data/1024/1024)
        sensors = psutil.sensors_temperatures()
        if("acpitz" in sensors):
            cpu_temp = str(psutil.sensors_temperatures().get("acpitz")[0].current)
        elif("cpu_thermal" in sensors):
            cpu_temp = str(psutil.sensors_temperatures().get("cpu_thermal")[0].current)
        else:
            cpu_temp = 0.0
        return cpu_percent,memory_percent,text_usage,data_usage,cpu_temp

    def getNetworkInfo():
        result = subprocess.run(['ip', 'route'], stdout=subprocess.PIPE)
        active = result.stdout.decode('utf-8').split("\n")[0]
        interface = active.split("dev ")[1].split(" proto")[0]
        interface = interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipaddr = s.getsockname()[0]
        ipaddr = ipaddr
        return interface,ipaddr

    def getUserInfo():
        user = os.getlogin()
        uid = str(os.getuid())
        gid = str(os.getgid())
        return user,uid,gid

    def getDateTimeInfo():
        day = datetime.now().strftime("%A")
        date = datetime.now().strftime("%d-%B-%Y")
        timenow = datetime.now().strftime("%H.%M.%S.%f")
        tzname = time.tzname[0]
        return day,date,timenow,tzname
