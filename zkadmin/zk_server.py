#encoding: utf-8
import re
import StringIO
import telnetlib

from kazoo.client import KazooClient

from json_handler import decode

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
        '''
        Telnet server to exec cmd 'stats' to get server mode(follower, standalone, leader).
        '''

        t = self.send_cmd('stats\n')
        mode = filter(lambda s:re.match(r'Mode: \w*$',s) , t.split("\n"))[0].split()[-1]
        return mode

    def get_info(self):
        '''
        Telnet server to exec cmd to get server basic info.
        '''

        self._get_stat()
        self._get_envi()
        self._get_dump()

    def _get_envi(self):
        '''
        Get ZooKeeper environment info.
        '''

        envi = self.send_cmd('envi\n')
        self.envi = []
        sio = StringIO.StringIO(envi)
        for line in sio:
            if not line.strip(): break
            attr, equ, value = line.partition("=")
            if not equ: continue
            self.envi.append((attr, value))

    def _get_dump(self):
        '''
        Get ZooKeeper ephemerals node count.
        '''

        dump = self.send_cmd('dump\n')
        self.emperemal_nodes = []
        sio = StringIO.StringIO(dump)
        for line in sio:
            m = re.match("Sessions with Ephemerals \((?P<name>\d*)\):", line)
            if m:
                self.ephemeralNum = int(m.group('name'))

    def _get_stat(self):
        '''
        Get ZooKeeper server basic stats.
        '''

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

    def __init__(self, leader_name, auth_data):
        self.zk = KazooClient(hosts=leader_name, auth_data=auth_data)
        self.zk.start()

    def exists_path(self, path):
        return  self.zk.exists(path)

    def get_children(self, path):
        if self.exists_path(path):
            self.children = self.zk.get_children(path)
            return self.children
        else:
            return False

    def get_info(self, path):
        if self.exists_path(path):
            return self.zk.get(path)

    def export_tree(self, path='/', ephemeral=False, name=None):
        '''
        Function: print tree of the children recursively, set given path as root.

        These two functions 'export_tree' and 'decode' belongs to @Jim Fulton's zc.zk(https://pypi.python.org/pypi/zc.zk/2.0.1).But Jim's code will raise a kazoo.error.NoAuth error when call get_children() of node has auth_data, i copy his code rather import it.
        '''

        output = []
        out = output.append
        def export_tree(path, indent, name=None):
            children = self.get_children(path)
            if path == '/':
                path = ''
                # if 'zookeeper' in children:
                #     children.remove('zookeeper')
                if name is not None:
                    out(indent + '/' + name)
                    indent += '  '
            else:
                data, meta = self.zk.get(path)
                if meta.ephemeralOwner and not ephemeral:
                    return
                if name is None:
                    name = path.rsplit('/', 1)[1]
                properties = decode(data)
                type_ = properties.pop('type', None)
                if type_:
                    name += ' : '+type_
                out(indent + '/' + name)
                indent += '  '
                links = []
                for i in sorted(properties.iteritems()):
                    if i[0].endswith(' ->'):
                        links.append(i)
                    else:
                        out(indent+"%s = %r" % i)
                for i in links:
                    out(indent+"%s %s" % i)

            for name in sorted(children):
                export_tree(path+'/'+name, indent)
        try:
            export_tree(path, '', name)
            return '\n'.join(output)+'\n'
        except Exception:
            return "No Auth To Show Tree."

    def __del__(self):
        self.zk.stop()

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
    
