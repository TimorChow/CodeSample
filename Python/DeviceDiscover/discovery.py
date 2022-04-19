"""
@author:
    xxxxxxxxxxx@gmail.com

@Description
    Discover all Server controlled by current PDU

@Process
    1. Turn off all port, Scan all device, get Non-server list
    2. Turn on all port, Scan all device, all All-Device list
    3. Figure out all Server list, create device object
    4. Turn off each one, and check which one disappear (with in Server list)
    5. There might be non-server in Device, ignore those that connected with multiple device
"""
import time
from typing import List, Dict

from device.models import Device, Status
from servers.models import Server
from watchdog.scan.utils import set_status, arp_scan

ServerType = Dict[str, Dict]


def get_diff(all_device: ServerType, non_miner: ServerType) -> ServerType:
    """
    Give two dict, return all different key-value

    :param all_device: A list of all discovered devices
    :param non_miner: A list of non-server devices
    :return: service devices = all-device - non-server
    """
    new_miner_dict = {}
    for _mac in all_device.keys():
        if _mac not in non_miner.keys():
            new_miner_dict[_mac] = all_device[_mac]
    return new_miner_dict


class Locator(object):
    def __init__(self):
        self.scanDeviceOffline = 60  # How long device will disappear in local network
        self.scanDeviceOnline = 60  # How long device will start and get a IP
        self.portCount = 48  # total port
        self.scanAllRepeat = 4  # for arp-scan command
        self.scan_history = []

    def get_miners(self):
        return Server.objects.filter(type__name='server').filter(id__lte=self.portCount)

    @staticmethod
    def scan(repeat=1):
        """
        Scan Multiple times, and return all current device
        [
            {
                'e8:10:sd:90:10': {
                    'mac': 'e8:10:sd:90:10',
                    'ip': '192.168.50.111',
                    'vendor': '(Unknown)'
                },
            },
        ]
        """
        result = {}
        for i in range(repeat):
            scan_result = arp_scan()
            for d in scan_result:
                result[d['mac']] = d
            if repeat != 1 and i != repeat - 1:
                time.sleep(10)

        return result

    def filter_extra(self):
        """
        Clean extra device
        1. Delete device that corresponding to multiple port
        2. If one port has two device, rescan it.
        """
        # 1. Delete
        for d in Device.objects.all():
            ports = d.ports.all()
            if len(ports) > 1:
                print("Device {} Deleted: {}".format(d.mac, ports))
                d.delete()

        # 2. Rescan
        def get_candidates() -> List[str]:
            """
            Get current incorrect devices (associate multiple port)
            """
            candidates = set()
            for m in self.get_miners():
                ports = m.devices.all()
                # 如果一个port有多个mac反应，保存这些mac
                if len(ports) >= 2:
                    for p in ports:
                        candidates.add(p.mac)
            return list(candidates)

        # If not candidates, exit
        if len(get_candidates()) == 0:
            return
        # 2.1 Open all port, mac should show up.
        cur_mac_list = self.scan().keys()
        for c in get_candidates():
            if c not in cur_mac_list:
                Device.objects.get(mac=c).delete()
                print(c, 'Deleted')

        # 2.2 Close all, mac should disappear
        self.get_miners().update(status=False)
        time.sleep(self.scanDeviceOffline)
        cur_mac_list = self.scan().keys()
        for c in get_candidates():
            if c in cur_mac_list:
                Device.objects.get(mac=c).delete()
                print(c, 'Deleted')

        # 2.3 Open all, mac should show up
        self.get_miners().update(status=True)
        time.sleep(self.scanDeviceOnline)
        cur_mac_list = self.scan().keys()
        for c in get_candidates():
            if c not in cur_mac_list:
                Device.objects.get(mac=c).delete()
                print(c, 'Deleted')

        print("Remain: ", get_candidates())

    def scan_port_check(self):
        """
        Turn Off each port and scan
        """
        self.scan_history.append(self.scan())
        for m in self.get_miners():
            loop_start = time.time()
            # A. Turn off server
            m.status = False
            m.save()
            time.sleep(self.scanDeviceOffline)

            # B2. compare with last scan
            self.scan_history.append(self.scan())
            off_macs: ServerType = get_diff(self.scan_history[-2], self.scan_history[-1])
            for mac in off_macs.keys():
                try:
                    d = Device.objects.get(mac=mac)
                    d.ports.add(m)
                    d.save()
                    print(m, mac, time.time() - loop_start)
                except:
                    continue

            m.status = True
            m.save()

    def ip_scan(self):
        """
        1. Turn off all port, Scan all device, get Non-server list
        2. Turn on all port, Scan all device, all All-Device list
        3. Figure out all Server list, create device object
        4. Turn off each one, and check which one disappear (with in Server list)
        5. There might be non-server in Device, ignore those that connected with multiple device
        """

        def create_device(new_miner_dict):
            """
            Create device candidates
            :param new_miner_dict:
            :return:
            """
            Device.objects.all().delete()
            for _, _d in new_miner_dict.items():
                device = Device()
                device.ip = _d['ip']
                device.mac = _d['mac']
                device.save()

        # 1. Turn off all device, and get all non-server device
        self.get_miners().update(status=False)
        time.sleep(self.scanDeviceOffline)
        non_miner_dict = self.scan(self.scanAllRepeat)
        print("Found Non-Server: {}".format(len(non_miner_dict)))

        # 2. Turn on all port, get all device
        self.get_miners().update(status=True)
        time.sleep(self.scanDeviceOnline)
        all_device_dict = self.scan()
        print("Found All Server: {}".format(len(all_device_dict)))

        # 3. get diff (Server list), and create object
        miner_dict = get_diff(all_device_dict, non_miner_dict)
        print("Found Server: {}".format(len(miner_dict)))
        create_device(miner_dict)

        # 4. Turn off each one
        self.scan_port_check()
        time.sleep(self.scanDeviceOnline)

        # 5. Filter non-server device
        self.filter_extra()
        print('Done Filter')


if __name__ == "__main__":
    print("isMinerDiscover Task is running!")
    start = time.time()
    locator = Locator()
    locator.ip_scan()
    print("isMinerDiscover End! took {}".format(time.time() - start))
