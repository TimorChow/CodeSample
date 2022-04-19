import os
import string
from typing import List, Dict

from device.models import Status
from service.SSHClient import SSHClient

PWD = os.getenv('SYSTEM_PASSWD')


def set_status(name, value):
    s = Status.objects.get(name=name)
    s.value = '1' if value else '0'
    s.save()


def arp_scan(r=2) -> List[Dict[string, string]]:
    """
    Access to host and get devices
    Return:
        [
            {
                'mac':      "a0:b0:45:00:bf:30",
                'ip':       "192.168.50.2",
                'vendor':   "(Unknown)",
            },
            ...
        ]
    """
    with SSHClient() as ssh:
        command = 'echo {pwd} | sudo -S arp-scan -l -r {R}'.format(pwd=PWD, R=r)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.readlines()
    devices = output[2: -3]
    result = []
    for d in devices:
        ip, mac, vendor = d.split("\t")
        result.append({
            'mac': mac,
            'ip': ip,
            'vendor': vendor
        })
    return result
