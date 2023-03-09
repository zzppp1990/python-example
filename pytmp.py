##eg1：
```
import errno
import logging
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
import uuid

import fcntl

from failover_dhcp_server import DnsmasqServer, DnsmasqHost
from failover_dhcpv6_server import Dnsmasq_Dhcpv6_Server, Dnsmasq_Dhcpv6_Host 

class DnsmasqWorker(object):
    def __init__(self):
        self.__normal_forward_feature = None
        self.__key_value_data = dict()
            
        cmd = 'ovs-vsctl --if-exists get bridge self.__br_name other_config:failover_type'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.__normal_forward_feature = stdout

    def run(self):
        if not self.__normal_forward_feature.strip() or self.__normal_forward_feature.strip() == u'normal-forward':
            self.__parse()
            if self.__key_value_data['operation'] == 'create_config':
                dnsmasq_server = DnsmasqServer(self.__key_value_data)
                dnsmasq_server.create()
            elif self.__key_value_data['operation'] == 'create_dhcpv6_config':
                dnsmasq_server = Dnsmasq_Dhcpv6_Server(self.__key_value_data)
                dnsmasq_server.create()
            elif self.__key_value_data['operation'] == 'destroy_config':
                dnsmasq_server = DnsmasqServer(self.__key_value_data)
                dnsmasq_server.destroy()
            elif self.__key_value_data['operation'] == 'destroy_dhcpv6_config':
                dnsmasq_server = Dnsmasq_Dhcpv6_Server(self.__key_value_data)
                dnsmasq_server.destroy()
            elif self.__key_value_data['operation'] == 'add_host':
                dnsmasq_host = DnsmasqHost(self.__key_value_data)
                dnsmasq_host.create()
            elif self.__key_value_data['operation'] == 'add_dhcpv6_host':
                dnsmasq_host = Dnsmasq_Dhcpv6_Host(self.__key_value_data)
                dnsmasq_host.create()
            elif self.__key_value_data['operation'] == 'del_host':
                dnsmasq_host = DnsmasqHost(self.__key_value_data)
                dnsmasq_host.destroy()
            elif self.__key_value_data['operation'] == 'del_dhcpv6_host':
                dnsmasq_host = Dnsmasq_Dhcpv6_Host(self.__key_value_data)
                dnsmasq_host.destroy()
            elif self.__key_value_data['operation'] == 'modify_config':
                dnsmasq_server = DnsmasqServer(self.__key_value_data)
                dnsmasq_server.modify()
            elif self.__key_value_data['operation'] == 'modify_dhcpv6_config':
                dnsmasq_server = Dnsmasq_Dhcpv6_Server(self.__key_value_data)
                dnsmasq_server.modify()
            elif self.__key_value_data['operation'] == 'modify_host':
                dnsmasq_host = DnsmasqHost(self.__key_value_data)
                dnsmasq_host.modify()
            elif self.__key_value_data['operation'] == 'modify_dhcpv6_host':
                dnsmasq_host = Dnsmasq_Dhcpv6_Host(self.__key_value_data)
                dnsmasq_host.modify()
            else:
                logging.error('[UNKNOWN CMD]')

    def __parse(self):
        logging.info('[DNSMASQ CMD] { %s }' % sys.argv[1:])
         
        for arg in sys.argv[1:]:
            key, value = arg.split('=', 1)
            self.__key_value_data[key] = value
            
         
        if 'options' in self.__key_value_data:
            option_key_value = self.__key_value_data.pop('options')
            option_key_value = filter(None, option_key_value.split(';'))
            for loop in option_key_value:
                key, value = loop.split('=', 1)
                self.__key_value_data[key] = value

        if 'ipv6-options' in self.__key_value_data:
            option_key_value = self.__key_value_data.pop('ipv6-options')
            option_key_value = filter(None, option_key_value.split(';'))
            for loop in option_key_value:
                key, value = loop.split('=', 1)
                self.__key_value_data[key] = value

        if 'other_config' in self.__key_value_data:
            other_config_key_value = self.__key_value_data.pop('other_config')
            other_config_key_value = filter(None, other_config_key_value.split(';'))
            for loop in other_config_key_value:
                key, value = loop.split('=', 1)
                self.__key_value_data[key] = value

if '__main__' == __name__:
    logging.basicConfig(filename='/var/log/openvswitch/dhcp-server.log', level=logging.INFO,
                        format='%(asctime)s %(process)d %(levelname)s: %(message)s')

    signal.signal(signal.SIGCHLD, signal.SIG_DFL)

    logging.info(sys.argv)

    try:
        DnsmasqWorker().run() 
    except Exception as e_global:
        logging.exception(e_global)


```

##eg2:
```
#! /usr/bin/env python
"""
Date 2017-05-03
"""
import errno
import logging
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
import uuid

import fcntl

from failover_dhcp_server_pub import DnsmasqException, DnsmasqUtils, Check, File, DirTransaction, FileTransaction,\
    DnsmasqInterfaceTransaction, RollBackSys, FlowManger, KeyValueBox, DnsmasqOptionEntry


######################################################
#################   server  part   ###################
######################################################

class DnsmasqServerOption(File):
    def __init__(self, filename):
        super(DnsmasqServerOption, self).__init__(filename)
        self.__public_db = dict()
        self.__host_db = dict()

    def load(self):
        super(DnsmasqServerOption, self).load()

        data = super(DnsmasqServerOption, self).get_data().split('\n')
        lines = filter(None, data)

        for line in lines:
            opt_entry = DnsmasqOptionEntry.value_of_line(line)
            if opt_entry.is_public():
                self.__public_db[opt_entry.get_protocol()] = opt_entry
            else:
                self.__host_db[opt_entry.get_tag()] = opt_entry

    def save(self, rbs=None):
        data = '\n'.join(map(str, self.__public_db.values()))
        data += ('\n' + '\n'.join(map(str, self.__host_db.values())))
        super(DnsmasqServerOption, self).set_data(data)

        try:
            super(DnsmasqServerOption, self).save()
        except IOError:
            logging.error('[DNSMASQSERVER][CREATE]<STOP> No such file { %s }!' % self.__filename)
            rbs.rollback()
            raise DnsmasqException()

    def __add_public(self, protocol, values, tag='public'):
        opt_entry = DnsmasqOptionEntry(tag, protocol, values)

        self.__public_db[protocol] = opt_entry
        
    def clear_public(self):
        self.__public_db.clear()
    
    def del_host_tag(self, tag):
        self.__host_db.pop(tag, 0)

    def add_public(self, key_value_data):
        if 'netmask' in key_value_data:
            self.__add_public('1', key_value_data['netmask'].split(','))

        if 'mtu' in key_value_data:
            self.__add_public('26', key_value_data['mtu'].split(','), 'mtu')

        if 'static_route' in key_value_data:
            self.__add_public('121', DnsmasqUtils.get_static_route(key_value_data['static_route']))

        option_key_value = {'server_id': '54', 'router': '3', 'lease': '51', 'domain_name': '15', 'dns': '6'}
        for key, value in option_key_value.items():
            if key in key_value_data:
                self.__add_public(value, key_value_data[key].split(','))

    def add_host(self, tag, mtu):
        host = DnsmasqOptionEntry(tag, '26', mtu.split(','))
        self.__host_db[tag] = host

    def del_host(self, tag):
        if tag in self.__host_db:
            self.__host_db.pop(tag)






class DnsmasqServerConfig(File):
    def __init__(self, filename):
        super(DnsmasqServerConfig, self).__init__(filename)
        self.__db = list()
        self.__config = None

        base_config = ['no-hosts', 'no-resolv', 'strict-order', 'bind-interfaces', 'dhcp-authoritative', 'log-dhcp']
        for element in base_config:
            self.__db.append(KeyValueBox(element))

        base_config = {'except-interface': 'lo', 'port': '0', 'log-facility': '/var/log/openvswitch/ovs-dnsmasq_dhcpv4.log'}
        for key, value in base_config.items():
            self.__db.append(KeyValueBox(key, value))

    def add_config(self, ip, port_name, base_file):
       
        self.__config = 'no-hosts;no-resolv;strict-order;bind-interfaces;except-interface=lo;port=0;' + \
                        'dhcp-range=' + ip + ',static;interface=' + port_name +  ';dhcp-authoritative' + \
                        ';log-dhcp;log-facility=/var/log/openvswitch/ovs-dnsmasq_dhcpv4.log'

        base_config = {'interface': port_name, 'dhcp-range': ip + ',static', 'pid-file': base_file['pid'],
                       'dhcp-hostsfile': base_file['host'], 'dhcp-optsfile': base_file['options'],
                       'dhcp-leasefile': base_file['lease']}
        

        for key, value in base_config.items():
            self.__db.append(KeyValueBox(key, value))

    def save(self, rbs=None):
        super(DnsmasqServerConfig, self).set_data('\n'.join(map(str, self.__db)))
        try:
            super(DnsmasqServerConfig, self).save()
        except IOError:
            logging.error('[DNSMASQSERVER][CREATE]<STOP> No such file { %s }!' % self.__filename)
            rbs.rollback()
            raise DnsmasqException()

    def get_config(self):
        return self.__config


class DnsmasqServer(object):
    def __init__(self, key_value_data):
        self.__base_dir = None
        self.__base_file = dict()
        self.__port_name = None
        self.__config = None

        if 'operation' in key_value_data:
            self.__operation = key_value_data['operation']
        else:
            self.__operation = None

        if 'uuid' in key_value_data:
            self.__uuid = key_value_data['uuid']
        else:
            self.__uuid = None

        if 'ip' in key_value_data:
            self.__ip = key_value_data['ip']
        else:
            self.__ip = None

        if 'br_name' in key_value_data:
            self.__br_name = key_value_data['br_name']
        else:
            self.__br_name = None

        if 'mac' in key_value_data:
            self.__mac = key_value_data['mac']
        else:
            self.__mac = None

        if 'segment_id' in key_value_data:
            self.__segment_id = key_value_data['segment_id']
        else:
            self.__segment_id = None

        self.__options = dict()
        if 'netmask' in key_value_data:
            self.__options['netmask'] = key_value_data['netmask']

        if 'server_id' in key_value_data:
            self.__options['server_id'] = key_value_data['server_id']

        if 'router' in key_value_data:
            self.__options['router'] = key_value_data['router']

        if 'mtu' in key_value_data:
            self.__options['mtu'] = key_value_data['mtu']

        if 'lease' in key_value_data:
            self.__options['lease'] = key_value_data['lease']

        if 'static_route' in key_value_data:
            self.__options['static_route'] = key_value_data['static_route']

        if 'domain_name' in key_value_data:
            self.__options['domain_name'] = key_value_data['domain_name']

        if 'dns' in key_value_data:
            self.__options['dns'] = key_value_data['dns']
			
    def create(self):
        self.__base_dir = DnsmasqUtils.get_base_dir(self.__uuid)
        self.__port_name = DnsmasqUtils.get_port_name_from_uuid(self.__uuid)

        if not os.path.exists('/var/run/openvswitch/dhcp_server/'):
            try:
                os.mkdir('/var/run/openvswitch/dhcp_server/', 755)
            except OSError:
                logging.error('[DNSMASQSERVER][CREATE] { /var/run/openvswitch } not exists!')
                raise DnsmasqException()
                
        if not os.path.exists(self.__base_dir):
            os.mkdir(self.__base_dir, 755)

        if os.path.exists(self.__base_dir + '/pid'):
            logging.info('[DNSMASQSERVER][RECOVER]<run>')
            self.__recover()
        else:
            logging.info('[DNSMASQSERVER][CREATE]<run>')
            self.__create()

        flow_manager = FlowManger.value_of_server(self.__br_name,
                                                  DnsmasqUtils.get_port_name_from_uuid(self.__uuid),
                                                  self.__segment_id)
        flow_manager.add_server_flow(self.__ip, self.__mac)
        self.write_back_info()

    def modify(self):
        self.__base_dir = DnsmasqUtils.get_base_dir(self.__uuid)
        self.__port_name = DnsmasqUtils.get_port_name_from_uuid(self.__uuid)

        if os.path.exists(self.__base_dir + '/pid'):
            logging.info('[DNSMASQSERVER][MODIFY]<run>')
            self.__modify()
        else:
            logging.error('[DNSMASQSERVER][MODIFY]<stop>')
            raise DnsmasqException()

    def __modify(self):
        rbs = RollBackSys()
        dir_base = DirTransaction(rbs, self.__base_dir)
        dir_base.register()

        self.__base_file['host'] = self.__base_dir + '/hostsfile'
        if not os.path.exists(self.__base_file['host']):
            logging.info('[DNSMASQSERVER][MODIFY] recover the file { %s }' % self.__base_file['host'])
            dir_host = DirTransaction(rbs, self.__base_file['host'])
            dir_host.make(register_rbs=False)

        dnsmasq_config_file = {'pid': '/pid', 'options': '/options', 'lease': '/lease', 'config': '/config'}
        for key, value in dnsmasq_config_file.items():
            self.__base_file[key] = self.__base_dir + value
            if not os.path.exists(self.__base_file[key]):
                logging.info('[DNSMASQSERVER][MODIFY] recover the file { %s }' % self.__base_file[key])
                config_file = FileTransaction(rbs, self.__base_dir + value)
                config_file.make()

        #modify server ip
        if isinstance(self.__ip, str):
            netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)
            port_name = DnsmasqUtils.get_port_name_from_uuid(self.__uuid)
            
            cmd = 'ip netns exec ' + netns + ' ip addr | grep global | grep -o /[0-9].'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            ip_cidr_sufix=stdout
            
            cmd = 'ip netns exec ' + netns + ' ifconfig ' + port_name + ' ' + self.__ip + ip_cidr_sufix
            exit_code = DnsmasqUtils.run_programs(cmd)
            if exit_code != 0:
                raise DnsmasqException()
            #options
            cmd = 'ovs-vsctl set dhcp_server ' + self.__uuid + ' options:router=' + self.__ip
            exit_code = DnsmasqUtils.run_programs(cmd)
            if exit_code != 0:
                raise DnsmasqException()
            #config file
            data = ''
            with open(self.__base_file['config'], 'r+') as f:
                for line in f.readlines():
                    print(line)
                    if (line.find('dhcp-range') == 0):
                       line = 'dhcp-range=%s,static' % self.__ip + '\n'
                    data += line

            with open(self.__base_file['config'], 'r+') as f:
                f.writelines(data)

            #default_config
            cmd = 'ovs-vsctl -fcsv -dbare --no-headings get dhcp_server ' + self.__uuid + ' default_config'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            default_config_old = stdout.strip('\n')
            default_config_new = re.sub(r'dhcp-range=.*,static','dhcp-range=' + self.__ip + ',static', default_config_old, count=1,flags=0)
            cmd = "ovs-vsctl set dhcp_server " + self.__uuid + " default_config='" + default_config_new + "'"
            exit_code = DnsmasqUtils.run_programs(cmd)
            if exit_code != 0:
                raise DnsmasqException()

        #modify options
        if len(self.__options):
            server_option = DnsmasqServerOption(self.__base_file['options'])
            server_option.load()
            server_option.clear_public()
            server_option.add_public(self.__options)
            server_option.save(rbs)

            netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)
            
        with open(self.__base_file['pid'], 'r') as f:
            pid = f.read()
            try:
                pid = int(pid)
                os.kill(pid, signal.SIGHUP)
            except (TypeError, ValueError, OSError):
                exit_code = DnsmasqUtils.run_programs('ip netns exec ' + netns + ' ovs-dnsmasq -C ' + self.__base_file['config'])
                if exit_code != 0:
                    rbs.rollback()

    def __recover(self):
        rbs = RollBackSys()

        dir_base = DirTransaction(rbs, self.__base_dir)
        dir_base.register()

        self.__base_file['host'] = self.__base_dir + '/hostsfile'
        if not os.path.exists(self.__base_file['host']):
            logging.info('[DNSMASQSERVER][RECOVER] recover the file { %s }' % self.__base_file['host'])
            dir_host = DirTransaction(rbs, self.__base_file['host'])
            dir_host.make(register_rbs=False)

        dnsmasq_config_file = {'pid': '/pid', 'options': '/options', 'lease': '/lease', 'config': '/config'}
        for key, value in dnsmasq_config_file.items():
            self.__base_file[key] = self.__base_dir + value
            if not os.path.exists(self.__base_file[key]):
                logging.info('[DNSMASQSERVER][RECOVER] recover the file { %s }' % self.__base_file[key])
                config_file = FileTransaction(rbs, self.__base_dir + value)
                config_file.make()

        with open(self.__base_file['pid'], 'r') as f:
            pid = f.read()
         
        server_config = DnsmasqServerConfig(self.__base_file['config'])
        server_config.add_config(self.__ip, self.__port_name, self.__base_file)
        server_config.save(rbs)
        self.__config = server_config.get_config()

        server_option = DnsmasqServerOption(self.__base_file['options'])
        server_option.load()
        server_option.add_public(self.__options)
        server_option.save(rbs)

        netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)
        ip_cidr = self.__ip + '/' + DnsmasqUtils.get_cidr(self.__options['netmask'])
        try:
            server_interface = DnsmasqInterfaceTransaction(rbs, netns, self.__br_name, self.__port_name, ip_cidr,
                                                           self.__mac)
            server_interface.recover()
        except DnsmasqException:
            try:
                pid = int(pid)
                os.kill(pid, signal.SIGKILL)
            except (TypeError, ValueError):
                logging.error('[DNSMASQSERVER][DESTROY] the pid in { %s } is Null!' % self.__base_file['pid'])
            except OSError:
                logging.error('[DNSMASQSERVER][DESTROY] the pid { %s } not exist in system.' % pid)

            return

        try:
            pid = int(pid)
            os.kill(pid, signal.SIGHUP)
        except (TypeError, ValueError, OSError):
            exit_code = DnsmasqUtils.run_programs(
                'ip netns exec ' + netns + ' ovs-dnsmasq -C ' + self.__base_file['config'])
            if exit_code != 0:
                rbs.rollback()

    def __create(self):
        rbs = RollBackSys()

        dir_base = DirTransaction(rbs, self.__base_dir)
        dir_base.register()

        self.__base_file['host'] = self.__base_dir + '/hostsfile'
        dir_host = DirTransaction(rbs, self.__base_file['host'])
        dir_host.make(register_rbs=False)

        dnsmasq_config_file = {'pid': '/pid', 'options': '/options', 'lease': '/lease', 'config': '/config'}
        for key, value in dnsmasq_config_file.items():
            self.__base_file[key] = self.__base_dir + value
            config_file = FileTransaction(rbs, self.__base_dir + value)
            config_file.make()
     
        server_config = DnsmasqServerConfig(self.__base_file['config'])
        server_config.add_config(self.__ip, self.__port_name, self.__base_file)
        server_config.save(rbs)
        self.__config = server_config.get_config()

        server_option = DnsmasqServerOption(self.__base_file['options'])
        server_option.add_public(self.__options)
        server_option.save(rbs)

        netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)        
        ip_cidr = self.__ip + '/' + DnsmasqUtils.get_cidr(self.__options['netmask'])            
        server_interface = DnsmasqInterfaceTransaction(rbs, netns, self.__br_name, self.__port_name, ip_cidr,
                                                       self.__mac)
        server_interface.make()

        # differentiate cas & centos because of 'unshare'
        cas_cvk_version_path = '/etc/cas_cvk-version'
        if os.path.exists(cas_cvk_version_path):
            exit_code = DnsmasqUtils.run_programs('unshare -m -- bash -c "mount | grep -vE \\"' + netns + '|on /run|on /var/log \\" | cut -d \' \' -f 3 | xargs -I {} umount -n {} 2>/dev/null;ip netns exec ' + netns + ' ovs-dnsmasq -C ' + self.__base_file['config'] + '"')
        else:
            exit_code = DnsmasqUtils.run_programs('ip netns exec ' + netns + ' ovs-dnsmasq -C ' + self.__base_file['config'])
        
        if exit_code != 0:
            rbs.rollback()

    def destroy(self):
        self.__base_dir = DnsmasqUtils.get_base_dir(self.__uuid)
        self.__port_name = DnsmasqUtils.get_port_name_from_uuid(self.__uuid)
        netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)
        pid_file = self.__base_dir + '/pid'

        if os.path.exists(pid_file):
            with open(pid_file, 'rb') as f:
                pid = f.read()
            try:
                pid = int(pid)
                os.kill(pid, signal.SIGKILL)
            except (TypeError, ValueError):
                logging.error('[DNSMASQSERVER][   ] the pid { %s } is Null!' % pid_file)
            except OSError:
                logging.error('[DNSMASQSERVER][DESTROY] the pid { %s } not exist in system.' % pid)

        else:
            logging.error('[DNSMASQSERVER][DESTROY] the pid file { %s } not exists!' % pid_file)

        flow_manager = FlowManger.value_of_server(self.__br_name,
                                                  DnsmasqUtils.get_port_name_from_uuid(self.__uuid),
                                                  self.__segment_id)
        flow_manager.del_server_flow(self.__ip)

        DnsmasqUtils.run_programs('ovs-vsctl del-port ' + self.__br_name + ' ' + self.__port_name)
        DnsmasqUtils.run_programs('ip netns delete ' + netns)

        shutil.rmtree(self.__base_dir, ignore_errors=True)

    def write_back_info(self):
        DnsmasqUtils.run_programs('ovs-vsctl set dhcp_server ' + self.__uuid + ' status=active' + ' external_ids:basedir="' + self.__base_dir + '"' + ' default_config=\'"' + self.__config + '"\'')


class DnsmasqHostConfig(File):
    def __init__(self, filename):
        self.__ip = None
        self.__mac = None
        self.__option = dict()
        self.__set = None
        super(DnsmasqHostConfig, self).__init__(filename)

    def load(self):
        super(DnsmasqHostConfig, self).load()
        lines = super(DnsmasqHostConfig, self).get_data().split('\n')
        lines = filter(None, lines)

        if len(lines) > 0:
            line = lines[0]
            for element in line.split(','):
                if Check.is_ip(element):
                    self.__ip = element
                elif Check.is_mac(element):
                    self.__mac = element
                elif Check.is_lease(element):
                    self.__option['lease'] = element
                elif Check.is_host_set(element):
                    self.__set = element
                else:
                    self.__option['hostname'] = element

    def modify(self, ip, mac, option, tag=None):
        self.__ip = ip
        self.__mac = mac
        self.__option = option
        if tag:
            self.__set = 'set:' + tag

    def save(self):
        line = self.__mac + ','
        line += 'set:public,'
        if self.__set:
            line += (self.__set + ',')        
        line += self.__ip          

        if 'hostname' in self.__option:
            line += (',' + self.__option['hostname'])

        if 'lease' in self.__option:
            line += (',' + self.__option['lease'])

        super(DnsmasqHostConfig, self).set_data(line)
        super(DnsmasqHostConfig, self).save()

    def get_mac(self):
        return self.__mac



class DnsmasqHost(object):
    def __init__(self, key_value_data):
        self.__base_dir = None
        self.__host_dir = None
        self.__dhcp_ofport = None

        if 'operation' in key_value_data:
            self.__operation = key_value_data['operation']
        else:
            self.__operation = None

        if 'uuid' in key_value_data:
            self.__uuid = key_value_data['uuid']
        else:
            self.__uuid = None

        if 'ip' in key_value_data:
            self.__ip = key_value_data['ip']
        else:
            self.__ip = None

        if 'mac' in key_value_data:
            self.__mac = key_value_data['mac']
        else:
            self.__mac = None

        if 'port_name' in key_value_data:
            self.__port_name = key_value_data['port_name']
        else:
            self.__port_name = None

        if 'vm_ofport' in key_value_data:
            self.__vm_ofport = key_value_data['vm_ofport']
        else:
            self.__vm_ofport = None
        
        if 'br_name' in key_value_data:
            self.__br_name = key_value_data['br_name']
        else:
            self.__br_name = None
            
        if 'segment_id' in key_value_data:
            self.__segment_id = key_value_data['segment_id']
        else:
            self.__segment_id = None
			        
        self.__options = dict()
        if 'mtu' in key_value_data:
            self.__options['mtu'] = key_value_data['mtu']
        if 'lease' in key_value_data:
            self.__options['lease'] = key_value_data['lease']
        if 'hostname' in key_value_data:
            self.__options['hostname'] = key_value_data['hostname']
		
        self.__dhcp_ofport = DnsmasqUtils.get_openflow_port(DnsmasqUtils.get_port_name_from_uuid(self.__uuid))
		        
    def destroy(self):
        rbs = RollBackSys()
        self.__base_dir = DnsmasqUtils.get_base_dir(self.__uuid)

        host_dir = self.__base_dir + '/hostsfile'
        if not os.path.exists(host_dir):
            logging.error('[DNSMASQHOST][DESTROY] the dir { %s } not exists!' % host_dir)
            raise DnsmasqException()

        host_config = DnsmasqHostConfig(host_dir + '/' + self.__port_name)
        host_config.load()
        mac = host_config.get_mac() 
        flow_manger = FlowManger.value_of_host(self.__br_name, None, self.__segment_id, self.__vm_ofport, self.__port_name, self.__dhcp_ofport, mac, self.__uuid)
        flow_manger.del_host_flow()

        try:
            os.remove(host_dir + '/' + self.__port_name)
        except OSError:
            pass

        lease_dir = self.__base_dir + '/lease'
        cmd = 'sed -i \'/' + self.__ip + '/d\' ' + lease_dir
        DnsmasqUtils.run_programs(cmd)
            
        option_file = self.__base_dir + '/options'
        if not os.path.exists(option_file):
            logging.error('[DNSMASQHOST][DESTROY] the file { %s } not exists!' % option_file)
            raise DnsmasqException()

        if 'mtu' in self.__options:
            server_option = DnsmasqServerOption(option_file)
            server_option.load()
            server_option.del_host(self.__port_name)
            server_option.save()

        netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)
        server_config_dir = self.__base_dir + '/config'

        with open(self.__base_dir + '/pid', 'r') as f:
            pid = f.read()
        try:
            pid = int(pid)
            os.kill(pid, signal.SIGKILL)
            exit_code = DnsmasqUtils.run_programs('ip netns exec ' + netns + ' ovs-dnsmasq -C ' + server_config_dir)
            if exit_code != 0:
                rbs.rollback()
        except (TypeError, ValueError):
            logging.error('[DNSMASQHOST][DESTROY] the pid in { %s } is Null!' % self.__base_dir + '/pid')
        except OSError:
            logging.error('[DNSMASQHOST][DESTROY] the pid { %s } not exist in system.' % pid)
            
    def create(self): 
        self.__base_dir = DnsmasqUtils.get_base_dir(self.__uuid)
        self.__host_dir = self.__base_dir + '/hostsfile'
        if not os.path.exists(self.__host_dir):
            logging.error('[DNSMASQHOST][CREATE] the dir { %s } not exists!' % self.__host_dir)
            raise DnsmasqException()

        if os.path.exists(self.__host_dir + '/' + self.__port_name):
            logging.info('[DNSMASQHOST][RECOVER]<run>')
            self.__recover()
        else:
            logging.info('[DNSMASQHOST][CREATE]<run>')
            self.__create()
                
    def modify(self):
        self.__base_dir = DnsmasqUtils.get_base_dir(self.__uuid)

        self.__host_dir = self.__base_dir + '/hostsfile'
        if not os.path.exists(self.__host_dir):
            logging.error('[DNSMASQHOST][MODIFY] the dir { %s } not exists!' % self.__host_dir)
            raise DnsmasqException()

        if os.path.exists(self.__host_dir + '/' + self.__port_name):
            logging.info('[DNSMASQHOST][MODIFY]<run>')
            self.__recover()
        else:
            logging.error('[DNSMASQHOST][MODIFY]<stop>')
            raise DnsmasqException()

       

    def __recover(self):
        option_file = self.__base_dir + '/options'
        if not os.path.exists(option_file):
            logging.error('[DNSMASQHOST][RECOVER] the file { %s } not exists!' % option_file)
            raise DnsmasqException()

        server_option = DnsmasqServerOption(option_file)
        server_option.load()
        server_option.del_host_tag(self.__port_name)
        
        if 'mtu' in self.__options:
            server_option.add_host(self.__port_name, self.__options['mtu'])
        
        server_option.save()


        flow_manger = FlowManger.value_of_host(self.__br_name, None, self.__segment_id, self.__vm_ofport, self.__port_name, self.__dhcp_ofport, self.__mac, self.__uuid)
        flow_manger.add_host_flow()
				        
        host_config = DnsmasqHostConfig(self.__host_dir + '/' + self.__port_name)
        host_config.load()
        mac = host_config.get_mac()
        if mac != self.__mac:                 
            flow_manger = FlowManger.value_of_host(self.__br_name, None, self_segment_id, self.__vm_ofport, self.__port_name, self.__dhcp_ofport, mac, self.__uuid)
            flow_manger.del_host_flow()
                
        if 'mtu' in self.__options:
            host_config.modify(self.__ip, self.__mac, self.__options, self.__port_name)
        else: 
            host_config.modify(self.__ip, self.__mac, self.__options)
        host_config.save()

        with open(self.__base_dir + '/pid', 'r') as f:
            pid = f.read()

        try:
            pid = int(pid)
            os.kill(pid, signal.SIGHUP)
        except (TypeError, ValueError):
            logging.error('[DNSMASQHOST][RECOVER] the pid in { %s } is Null!' % self.__base_dir + '/pid')
        except OSError:
            logging.error('[DNSMASQHOST][RECOVER] the pid { %s } not exist in system.' % pid)

    def __create(self):
        rbs = RollBackSys()
        host_file = FileTransaction(rbs, self.__host_dir + '/' + self.__port_name)
        host_file.make(register_rbs=True)

        option_file = self.__base_dir + '/options'
        if not os.path.exists(option_file):
            logging.error('[DNSMASQHOST][CREATE] the file { %s } not exists!' % option_file)
            rbs.rollback()
            raise DnsmasqException()

        if 'mtu' in self.__options:
            server_option = DnsmasqServerOption(option_file)
            server_option.load()
            server_option.add_host(self.__port_name, self.__options['mtu'])
            server_option.save()
	else:
            self.__options['mtu'] = None		 

        host_config = DnsmasqHostConfig(self.__host_dir + '/' + self.__port_name)

        if 'mtu' in self.__options:
            host_config.modify(self.__ip, self.__mac, self.__options, self.__port_name)
        else:
            host_config.modify(self.__ip, self.__mac, self.__options)      
        host_config.save()

        with open(self.__base_dir + '/pid', 'r') as f:
            pid = f.read()

        try:
            pid = int(pid)
            os.kill(pid, signal.SIGHUP)
        except (TypeError, ValueError):
            logging.error('[DNSMASQHOST][CREATE] the pid in { %s } is Null!' % self.__base_dir + '/pid')
        except OSError:
            logging.error('[DNSMASQHOST][CREATE] the pid { %s } not exist in system.' % pid)
 
        flow_manger = FlowManger.value_of_host(self.__br_name, None, self.__segment_id, self.__vm_ofport, self.__port_name, self.__dhcp_ofport, self.__mac, self.__uuid)
        flow_manger.add_host_flow()


```

##eg3:
```

import errno
import logging
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
import uuid

import fcntl



class DnsmasqException(Exception):
    pass


class DnsmasqUtils(object):
    @staticmethod
    def get_port_name_from_uuid(dhcp_uuid):
        return 'vp-' + dhcp_uuid.split('-')[4]

    @staticmethod
    def get_netns_name_from_uuid(dhcp_uuid):
        return 'flow_dhcp-' + dhcp_uuid

    @staticmethod
    def __run_program(cmd):
        logging.info('[RUN PROGRAM] { %s }' % cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exit_code = process.returncode
        if exit_code != 0:
            logging.error('[PROGRAM STDERR] { %s }' % stderr)

        return exit_code

    @staticmethod
    def run_programs(cmds):
        if isinstance(cmds, str):
            return DnsmasqUtils.__run_program(cmds)

        if isinstance(cmds, list):
            for cmd in cmds:
                DnsmasqUtils.__run_program(cmd)

    @staticmethod
    def get_static_route(static_route):
        if isinstance(static_route, str):
            elements = static_route.split(',')
        else:
            elements = static_route

        return [','.join(n) for n in zip(elements[::2], elements[1::2])]

    @staticmethod
    def get_base_dir(dhcp_uuid):
        return '/var/run/openvswitch/dhcp_server/' + dhcp_uuid

    @staticmethod
    def get_cidr(netmask):

        netmask = struct.unpack('!I', socket.inet_aton(netmask))[0]
        return str(bin(netmask).count('1'))

    @staticmethod
    def get_openflow_port(port_name):
        cmd = 'ovs-vsctl get interface ' + port_name + ' ofport'
        logging.info('[RUN PROGRAM] { %s }' % cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exit_code = process.returncode

        if exit_code != 0:
            logging.error('[PROGRAM STDERR] { %s }' % stderr)
            return None
        else:
            return stdout.rstrip('\n')


class Check(object):
    @staticmethod
    def is_uuid(dhcp_uuid):
        try:
            uuid.UUID(dhcp_uuid)
        except (ValueError, TypeError):
            return False

        return True

    @staticmethod
    def is_ip(ip):
        if not isinstance(ip, str):
            return False

        if ip.count('.') != 3:
            return False
        else:
            try:
                socket.inet_aton(ip)
            except socket.error:
                return False

        return True

    @staticmethod
    def is_mac(mac):
        if not isinstance(mac, str):
            return False

        return bool(re.match('^[0-9a-f]{2}(:[0-9a-f]{2}){5}$', mac.lower()))

    @staticmethod
    def is_lease(dhcp_lease):
        try:
            dhcp_lease = int(dhcp_lease)
        except ValueError:
            return False

        if dhcp_lease <= 120:
            return False
        else:
            return True

    @staticmethod
    def is_host_set(host_set):
        if not isinstance(host_set, str):
            return False

        if not host_set.startswith('set:'):
            return False

        if host_set.startswith('set:public'):
            return False
        else:
            return True

    @staticmethod
    def is_bridge_name(bridge_name):
        if not isinstance(bridge_name, str):
            return False

        # the length of bridge name must be less then 16.
        if 0 < len(bridge_name) < 16:
            # test whether bridge name exists as a real or fake bridge.
            exit_code = DnsmasqUtils.run_programs('ovs-vsctl br-exists ' + bridge_name)
            if exit_code == 0:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def is_netmask(netmask):
        if not isinstance(netmask, str):
            return False

        if not Check.is_ip(netmask):
            return False

        netmask = struct.unpack('!I', socket.inet_aton(netmask))[0]
        cidr = bin(netmask).count('1')
        cidr = (1 << 32) - (1 << (32 - cidr))

        return netmask == cidr

    @staticmethod
    def is_mtu(mtu):
        if not isinstance(mtu, str):
            return False

        try:
            mtu = int(mtu)
        except ValueError:
            return False

        if 1 < mtu < 65536:
            return True
        else:
            return False

    @staticmethod
    def is_static_route(static_route):
        if not isinstance(static_route, str):
            return False

        elements = static_route.split(',')

        if ((len(elements) % 2) != 0) or (len(elements) < 2):
            return False
        else:
            elements = [','.join(n) for n in zip(elements[::2], elements[1::2])]
            for element in elements:
                cidr, next_hop = element.split(',')
                if not Check.is_ip(next_hop):
                    return False

                ip, cidr = cidr.split('/')

                if not Check.is_ip(ip):
                    return False

                try:
                    cidr = int(cidr)
                except (ValueError, TypeError):
                    return False

                if cidr < 0 or cidr > 32:
                    return False

        return True

    @staticmethod
    def is_set(host_set):
        if not isinstance(host_set, str):
            return False
        return host_set.startswith('set:')

    @staticmethod
    def is_ofport(ofport):
        if not isinstance(ofport, str):
            return False
        try:
            ofport = int(ofport)
        except ValueError:
            return False

        return 0 < ofport

    @staticmethod
    def is_segment_id(segment_id):
        if not isinstance(segment_id, str):
            return False
        try:
            segment_id = int(segment_id)
        except ValueError:
            return False

        return 0 < segment_id < 16777216


class File(object):
    def __init__(self, filename):

        if filename:
            self.__filename = filename
            self.__data = None
        else:
            raise ValueError()

    def load(self):
        with open(self.__filename, 'r') as f:
            self.__data = f.read()

    def save(self):
        with open(self.__filename, 'w') as f:
            f.write(self.__data)

    def set_data(self, data):
        self.__data = data

    def get_data(self):
        return self.__data


class DirTransaction(object):
    def __init__(self, roll_back_sys, local_dir):
        if not local_dir.startswith('/var/run/openvswitch/dhcp_server/'):
            logging.error('[DNSMASQSERVER][CREATE]<STOP> the dir { %s } is invalid!' % local_dir)
            roll_back_sys.rollback()
            raise DnsmasqException()
        self.__local_dir = local_dir
        self.__roll_back_sys = roll_back_sys

    def make(self, register_rbs=True):
        try:
            os.mkdir(self.__local_dir, 0755)
        except OSError:
            self.__roll_back_sys.rollback()
            raise DnsmasqException()

        if register_rbs:
            self.__roll_back_sys.add_transaction(self)

    def register(self):
        self.__roll_back_sys.add_transaction(self)

    def rollback(self):
        logging.error('[DNSMASQ][ROLLBACKSYS] del dir { %s }.' % self.__local_dir)
        shutil.rmtree(self.__local_dir, ignore_errors=True)


class FileTransaction(object):
    def __init__(self, roll_back_sys, local_file):
        if not local_file.startswith('/var/run/openvswitch/dhcp_server/'):
            logging.error('[DNSMASQSERVER][ROLLBACKSYS]<STOP> the file { %s } is invalid!' % local_file)
            roll_back_sys.rollback()
            raise DnsmasqException()
        self.__local_file = local_file
        self.__roll_back_sys = roll_back_sys

    def make(self, register_rbs=False):
        try:
            os.mknod(self.__local_file, 0644)
        except OSError:
            self.__roll_back_sys.rollback()
            raise DnsmasqException()

        if register_rbs:
            self.__roll_back_sys.add_transaction(self)

    def rollback(self):
        logging.error('[DNSMASQ][ROLLBACKSYS] del file { %s }.' % self.__local_file)
        try:
            os.rmdir(self.__local_file)
        except OSError:
            pass


class DnsmasqInterfaceTransaction(object):
    def __init__(self, roll_back_sys, netns, br_name, port_name, ip_cidr, mac):
        self.__make_cmds = list()
        self.__rollback_cmds = list()
        self.__roll_back_sys = roll_back_sys

        self.__netns = netns
        self.__br_name = br_name
        self.__port_name = port_name
        self.__ip_cidr = ip_cidr
        self.__mac = mac
        
        self.__make_cmds.append('ovs-vsctl --may-exist add-port ' + br_name + ' ' + port_name
                                + ' -- set interface ' + port_name + ' type=internal')
        self.__make_cmds.append('ip netns add ' + netns)
        self.__make_cmds.append('ip link set ' + port_name + ' netns ' + netns)
        self.__make_cmds.append('ip netns exec ' + netns + ' ip link set dev ' + port_name + ' address ' + mac)
        self.__make_cmds.append('ip netns exec ' + netns + ' ip link set dev ' + port_name + ' up')
        if ip_cidr !=None:
            self.__make_cmds.append('ip netns exec ' + netns + ' ip addr add ' + ip_cidr + ' dev ' + port_name)
        self.__rollback_cmds.append('ovs-vsctl del-port ' + br_name + ' ' + port_name)
        self.__rollback_cmds.append('ip netns delete ' + netns)

    def make(self, register_rbs=True):
        for cmd in self.__make_cmds:
            exit_code = DnsmasqUtils.run_programs(cmd)
            if exit_code != 0:
                self.rollback()
                self.__roll_back_sys.rollback()
                raise DnsmasqException()

        if register_rbs:
            self.__roll_back_sys.add_transaction(self)

    def recover(self):
        exit_code = DnsmasqUtils.run_programs('ovs-vsctl list-ports ' + self.__br_name + ' | grep ' + self.__port_name)
        if exit_code != 0:
            if __name__ == '__main__':
                self.make()
        else:
            exit_code = DnsmasqUtils.run_programs('ip netns list | grep ' + self.__netns)
            if exit_code != 0:
                for cmd in self.__make_cmds[1:]:
                    exit_code = DnsmasqUtils.run_programs(cmd)
                    if exit_code != 0:
                        self.rollback()
                        self.__roll_back_sys.rollback()
                        raise DnsmasqException()
                return

            exit_code = DnsmasqUtils.run_programs(
                'ip netns exec ' + self.__netns + ' ip link list dev ' + self.__port_name)
            if exit_code != 0:
                for cmd in self.__make_cmds[2:]:
                    exit_code = DnsmasqUtils.run_programs(cmd)
                    if exit_code != 0:
                        self.rollback()
                        self.__roll_back_sys.rollback()
                        raise DnsmasqException()
                return

            for cmd in self.__make_cmds[3:-1]:
                exit_code = DnsmasqUtils.run_programs(cmd)
                if exit_code != 0:
                    self.rollback()
                    self.__roll_back_sys.rollback()
                    raise DnsmasqException()

            if  self.__ip_cidr is not None:
                exit_code = DnsmasqUtils.run_programs(
                    'ip netns exec ' + self.__netns +
                    ' ip -o -4 addr list ' + self.__port_name + '  | awk \'{print $4}\' | grep ' + self.__ip_cidr)
                if exit_code != 0:
                    exit_code = DnsmasqUtils.run_programs(self.__make_cmds[-1])
                    if exit_code != 0:
                        self.rollback()
                        self.__roll_back_sys.rollback()
                        raise DnsmasqException()

    def rollback(self):
        for cmd in self.__rollback_cmds:
            DnsmasqUtils.run_programs(cmd)


class RollBackSys(object):
    def __init__(self):
        self.__stack = list()

    def add_transaction(self, transaction):
        self.__stack.append(transaction)

    def rollback(self):
        logging.error('[DNSMASQ][ROLLBACKSYS]<rollback>')
        for transaction in reversed(self.__stack):
            transaction.rollback()


class FlowManger(object):
    def __init__(self, br_name, dhcp_port_name=None, segment_id=None, vm_ofport=None, vm_port_name=None, dhcp_ofport=None, mac=None, uuid=None):
        self.__br_name = br_name
        self.__vm_ofport = vm_ofport
        self.__vm_port_name = vm_port_name
        self.__dhcp_ofport = dhcp_ofport
        self.__dhcp_port_name = dhcp_port_name
        self.__mac = mac
        self.__segment_id = segment_id
        self.__normal_forward_feature = None
        self.__uuid = uuid
        if self.__uuid != None:
            self.__netns = DnsmasqUtils.get_netns_name_from_uuid(self.__uuid)

        cmd = 'ovs-vsctl --if-exists get bridge ' +  self.__br_name + ' other_config:failover_type'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.__normal_forward_feature = stdout
        
    @classmethod
    def value_of_server(cls, br_name, dhcp_port_name, segment_id):
        obj = cls(br_name, dhcp_port_name, segment_id)
        return obj

    @classmethod
    def value_of_host(cls, br_name, dhcp_port_name, segment_id, vm_ofport, vm_port_name, dhcp_ofport, mac, uuid):
        obj = cls(br_name, dhcp_port_name, segment_id, vm_ofport, vm_port_name, dhcp_ofport, mac, uuid)

        return obj

    def add_server_flow(self, server_ip, vmac):
        if not self.__normal_forward_feature.strip():
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/dhcp_add_subnet_flows.sh ' +
                                      self.__br_name + ' ' + self.__dhcp_port_name + ' ' + self.__segment_id + ' ' + server_ip + ' ' + vmac)
    def add_ipv6_server_flow(self):
        DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcpv6_add_server_flows.sh ' +
                                  self.__br_name + ' ' + self.__dhcp_port_name + ' ' + self.__segment_id + ' ')
    def del_server_flow(self, server_ip):
        if not self.__normal_forward_feature.strip():
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/dhcp_del_subnet_flows.sh ' +
                                      self.__br_name + ' ' + self.__dhcp_port_name + ' ' + self.__segment_id + ' ' + server_ip)
    def del_ipv6_server_flow(self):
        DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcpv6_del_server_flows.sh ' +
                                  self.__br_name + ' ' + self.__dhcp_port_name + ' ' + self.__segment_id + ' ')
    def add_host_flow(self):
        if not self.__normal_forward_feature.strip():
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/dhcp_add_client_flows.sh ' + self.__br_name + ' ' +
                                      self.__vm_ofport + ' ' + self.__dhcp_ofport + ' ' + self.__mac)
        else:
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcp_add_client_flows.sh ' + self.__br_name + ' ' +
                                      self.__vm_port_name + ' ' + self.__vm_ofport + ' ' + self.__dhcp_ofport + ' ' + self.__mac + ' ' + self.__segment_id)
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcp_add_flood_flows.sh ' + self.__br_name + ' ' +
                                      self.__dhcp_ofport)
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcp_flood_add_port_groups.sh ' + self.__br_name + ' ' +
                                      self.__dhcp_ofport + ' ' + self.__vm_port_name + ' ' + self.__vm_ofport)
    def add_ipv6_host_flow(self):
        DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcpv6_add_client_flows.sh ' + self.__br_name + ' ' + self.__segment_id + ' ' + 
                                      self.__vm_port_name + ' ' + self.__vm_ofport + ' ' + self.__dhcp_ofport + ' ' + self.__mac + ' '  + self.__dhcp_port_name)

    def del_host_flow(self):
        if not self.__normal_forward_feature.strip():
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/dhcp_del_client_flows.sh ' + self.__br_name + ' ' +
                                      self.__vm_ofport + ' ' + self.__dhcp_ofport + ' ' + self.__mac)
        else:
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcp_del_client_flows.sh ' + self.__br_name + ' ' +self.__vm_port_name + ' ' +
                                      self.__vm_ofport + ' ' + self.__dhcp_ofport + ' ' + self.__mac + ' ' + self.__uuid + ' ' + self.__segment_id)
            DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcp_flood_del_port_groups.sh ' + self.__br_name + ' ' +
                                      self.__dhcp_ofport + ' ' + self.__vm_ofport)

    def del_ipv6_host_flow(self):
        DnsmasqUtils.run_programs('/usr/share/openvswitch/scripts/normal_forward_dhcpv6_del_client_flows.sh ' + self.__br_name + ' ' +self.__vm_port_name + ' ' + 
                                      self.__vm_ofport + ' ' + self.__dhcp_ofport + ' ' + self.__mac +  ' ' + self.__dhcp_port_name + ' ' + self.__segment_id)

class KeyValueBox(object):
    def __init__(self, key, value=None):
        self.__key = key
        self.__value = value

    def __str__(self):
        if self.__value:
            return '='.join((self.__key, self.__value))
        else:
            return self.__key


class DnsmasqOptionEntry(object):
    def __init__(self, tag, protocol, value):
        self.__tag = tag
        self.__protocol = protocol
        self.__value = value

    def __str__(self):
        return 'tag:' + self.__tag + ',' + self.__protocol + ',' + ','.join(self.__value)

    @classmethod
    def value_of_line(cls, line):
        elements = line.split(',')

        if '121' == elements[1]:
            obj = cls(elements[0].replace('tag:', ''), elements[1], DnsmasqUtils.get_static_route(elements[2:]))
        else:
            obj = cls(elements[0].replace('tag:', ''), elements[1], elements[2:])

        return obj

    def is_public(self):

        return (self.__tag == 'public') or (self.__tag == 'mtu')

    def get_protocol(self):
        return self.__protocol

    def get_tag(self):
        return self.__tag

```

