#encoding: utf-8 

from zk_server import ZKServer, ZNode
from servers import ZOOKEEPER_SERVERS

class ZKCluster(object):

    def __init__(self, cluster_name):
        '''
        Config cluster with cluster_name, and choose leader node's info as the latest view by the config file: servers.py automatically.   
        '''

        self.cluster_name = cluster_name
        self.server_list = self.get_server()
        self.auth_data = self._get_auth_data()
        self.znode = ZNode(self.node['leader'], self.auth_data)

    @property
    def leader(self):
        '''
        If the cluster_name is not pointed to a cluster but a single host, the leader node is the STANDALONE node.
        '''

        mode = self.node['leader'] != None and self.node['leader'] or self.node['standalone']
        z = ZKServer(mode)
        z.get_info()
        return z

    def _get_auth_data(self):
        return ZOOKEEPER_SERVERS[self.cluster_name]['auth_data']

    def get_server(self):
        '''
        Get cluster's servers list, and classify them to follower, leader, standalone.
        '''

        server_list = []
        self.node = {'follower':[], 'leader':None, 'standalone':None}
        for each in ZOOKEEPER_SERVERS[self.cluster_name]['servers']:
            server = ZKServer(each)
            if server.mode == "follower" :
                self.node['follower'].append(each)
            else:
                self.node['leader'] = each
            server_list.append(each)
        return server_list

def main():
    import re
    #zs = ZKServer("cloudcomputing-zookeeper-online001-bjdxt.qiyi.virtual:2181")
    zs = ZKCluster("bj")
    print zs.leader.mode, zs.leader.port

if __name__ == '__main__':
    main()
    
