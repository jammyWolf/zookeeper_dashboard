from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

from zookeeper_dashboard.zkadmin.models import ZKServer
from zknode import ZNode
from models import ZKCluster

from servers import ZOOKEEPER_SERVERS

def getCluster(cluster_name, path):
    zk_cluster = ZKCluster(cluster_name)
    server_data = zk_cluster.cluster(ZOOKEEPER_SERVERS[cluster_name])
    for e in server_data:
        if e.mode == 'leader':
            leader_data = e
            break
    try:
        leader_url = leader_data.host+':'+leader_data.port
    except:
        leader_url = ZOOKEEPER_SERVERS[cluster_name][0]
    znode = ZNode(leader_url, path)
    return server_data, znode

def index(request):
    return render_to_response('zkadmin/index.html',
                              {'server_data':ZOOKEEPER_SERVERS.keys()},context_instance=RequestContext(request) )

def detail(request, cluster_name):
    path = '/'
    if request.POST != [] and 'path' in request.POST:
        path=request.POST['path']
    server_data, znode = getCluster(cluster_name, path)
    return render_to_response('zkadmin/detail.html',
            {'server_data':server_data, 'znode':znode, 'cluster_name':cluster_name})
