import re
import StringIO
import telnetlib

from servers import ZOOKEEPER_SERVERS
OP_READ = 1
OP_WRITE = 4
OP_CONNECT = 8
OP_ACCEPT = 16

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
        try:
            stat = self.send_cmd('stat\n')
            envi = self.send_cmd('envi\n')
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
            if not line.strip():
                break
            self.sessions.append(Session(line.strip()))
        for line in sio:
            attr, value = line.split(':')
            attr = attr.strip().replace(" ", "_").replace("/", "_").lower()
            print attr, value
            self.__dict__[attr] = value.strip()

        self.min_latency, self.avg_latency, self.max_latency = self.latency_min_avg_max.split("/")

        self.envi = []
        sio = StringIO.StringIO(envi)
        for line in sio:
            if not line.strip(): break
            attr, equ, value = line.partition("=")
            if not equ: continue
            self.envi.append((attr, value))

    def send_cmd(self, cmd):
        tn = telnetlib.Telnet(self.host, self.port)
        tn.write(cmd)
        result = tn.read_all()
        tn.close()
        return result

def main():
    zk_cluster = ZKCluster("me")
    server_data = zk_cluster.cluster(ZOOKEEPER_SERVERS['me'])
    # print dir(server_data)
    # for e in server_data:
    #     print e.node_count
    #     if e.mode == 'leader':
    #         leader_data = e
    #         break
    #         'connections', 'envi', 'host','mode', 'node_count', 'port', 'received', 'sent', 'version'
    # print leader_data.connections
    # print leader_data.envi
    # print leader_data.node_count
    # print leader_data.received
        # try:
        #     leader_url = leader_data.host+':'+leader_data.port
        # except:
        #     leader_url = ZOOKEEPER_SERVERS[cluster_name][0]
        # znode = ZNode(leader_url, path)
        # return server_data, znode

if __name__ == '__main__':
    main()
