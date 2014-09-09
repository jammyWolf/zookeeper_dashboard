from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

from zk_cluster import ZKCluster
from servers import ZOOKEEPER_SERVERS

def index(request):
    cluster_info = []
    for k, v in ZOOKEEPER_SERVERS.iteritems(): 
        info = {}
        zk_cluster = ZKCluster(k)
        info['cluster_name'] = k
        info['node_count'] = zk_cluster.leader.node_count
        info['ephemeral_count'] = zk_cluster.leader.ephemeralNum
        cluster_info.append(info)
    return render_to_response('zkadmin/index.html',
                              {'cluster_info':cluster_info}, context_instance=RequestContext(request) )

def detail(request, cluster_name):
    path = '/'
    if request.POST != [] and 'path' in request.POST:
        path=request.POST['path']
    zk = ZKCluster(cluster_name)
    znode = zk.znode
    children = znode.get_children(path)
    tree = znode.export_tree(path)
    if path == "/":
        server_data =  zk.leader
    else:
        data, stat = znode.get_info(path)
    
    return render_to_response('zkadmin/detail.html',
           locals())

