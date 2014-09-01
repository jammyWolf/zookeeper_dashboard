#encoding: utf-8
import re
import StringIO
import telnetlib

import kazoo
from kazoo.protocol.states import ZnodeStat
from kazoo.client import KazooClient, KazooState, KeeperState

from servers import ZOOKEEPER_SERVERS

class Session(object):
    def __init__(self, session):
        m = re.search('/(\d+\.\d+\.\d+\.\d+):(\d+)\[(\d+)\]\((.*)\)', session)
        self.host = m.group(1)
        self.port = m.group(2)
        self.interest_ops = m.group(3)
        for d in m.group(4).split(","):
            k,v = d.split("=")
            self.__dict__[k] = v

class ZKServer(object):

    def __init__(self, server):
        self.host, self.port = server.split(':')

    @property
    def mode(self):
        t = self.send_cmd('stats\n')
        mode = filter(lambda s:re.match(r'Mode: \w*$',s) , t.split("\n"))[0].split()[-1]
        return mode

    def get_info(self):
        self._get_stat()
        self._get_envi()
        self._get_dump()

    def _get_envi(self):
        envi = self.send_cmd('envi\n')
        self.envi = []
        sio = StringIO.StringIO(envi)
        for line in sio:
            if not line.strip(): break
            attr, equ, value = line.partition("=")
            if not equ: continue
            self.envi.append((attr, value))

    def _get_dump(self):
        dump = self.send_cmd('dump\n')
        self.emperemal_nodes = []
        sio = StringIO.StringIO(dump)
        for line in sio:
            m = re.match("Sessions with Ephemerals \((?P<name>\d*)\):", line)
            if m:
                self.ephemeralNum = int(m.group('name'))

    def _get_stat(self):
        try:
            stat = self.send_cmd('stat\n')
        except:
            self.mode = "Unavailable"
            self.sessions = []
            self.version = "Unknown"
            return

        sio = StringIO.StringIO(stat)
        line = sio.readline()
        m = re.search('.*: (\d+\.\d+\.\d+)-.*', line)
        self.version = m.group(1)
        sio.readline()
        self.sessions = []
        for line in sio:
            if not line.strip(): #break enters \n
                break
            self.sessions.append(Session(line.strip()))
        for line in sio:
            attr, value = line.split(':')
            attr = attr.strip().replace(" ", "_").replace("/", "_").lower()
            self.__dict__[attr] = value.strip()

        self.min_latency, self.avg_latency, self.max_latency = self.latency_min_avg_max.split("/")

    def send_cmd(self, cmd):
        tn = telnetlib.Telnet(self.host, self.port)
        tn.write(cmd)
        result = tn.read_all()
        tn.close()
        return result

class ZNode(object):

    def __init__(self, leader_name, path="/"):
        self.zk = KazooClient(hosts=leader_name, auth_data=[("digest","transcode:vtc" )]
                )
        self.zk.start()

    def ensure_path(self, path):
        return  self.zk.ensure_path(path)

    def children(self, path):
        if self.ensure_path(path):
            self.children = self.zk.get_children(path)
            return self.children
        else:
            return False

    def get_info(self, path):
        if self.ensure_path(path):
            #return data, stat
            return self.zk.get(path)

    def __del__(self):
        self.zk.stop()

class ZKCluster(object):

    def __init__(self, cluster_name):
        self.cluster_name = cluster_name
        self.server_list = self.get_server()
        self.znode = ZNode(self.node['leader'])

    @property
    def leader(self):
        mode = self.node['leader'] != None and self.node['leader'] or self.node['standalone']
        z = ZKServer(mode)
        z.get_info()
        return z

    def get_server(self):
        server_list = []
        self.node = {'follower':[], 'leader':None, 'standalone':None}
        for each in ZOOKEEPER_SERVERS[self.cluster_name]:
            server = ZKServer(each)
            if server.mode == "follower" :
                self.node['follower'].append(each)
            else:
                self.node['leader'] = each
            server_list.append(each)
        return server_list

def main():
    #zs = ZKServer("cloudcomputing-zookeeper-online001-bjdxt.qiyi.virtual:2181")
    zs = ZKCluster("bj")
    z = zs.leader_info
    z.get_info()
    #for each in dir(z):
    #    if re.match("^[^_].*$", each):
    #        print each, getattr(z, each)
    for e in z.sessions:
        for i in dir(e):
            if re.match("^[^_].*$", i):
                print i, getattr(e, i)
    #print dir(z) 
    #zs.get_info()
    #print dir(zs)

if __name__ == '__main__':
    main()
    
