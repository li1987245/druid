# coding=utf-8
from zlib import crc32

def lcs():
    s1 = [1, 3, 4, 5, 6, 7, 7, 8]  # 3,4,6,7,8
    s2 = [3, 5, 7, 4, 8, 6, 7, 8, 2]

    d = [[0] * (len(s2) + 1) for i in range(len(s1) + 1)]

    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                d[i][j] = d[i - 1][j - 1] + 1
            else:
                d[i][j] = max(d[i - 1][j], d[i][j - 1])

    print "max LCS number:", d[-1][-1]  # 5
    tmp = d[len(s1)][len(s2)]
    i = len(s1)
    j = len(s2)
    while len(s1) >= i > 0 and len(s2) >= j > 0:
        if d[i - 1][j] != tmp and d[i][j - 1] != tmp:
            print s1[i - 1], s2[j - 1]
            i -= 1
            j -= 1
            tmp = d[i][j]
        else:
            if d[i - 1][j] == tmp:
                i -= 1
            elif d[i][j - 1] == tmp:
                j -= 1

def sharding(key):
    pass
class HashConsistency(object):
    def __init__(self, nodes=None, replicas=5):
        # 虚拟节点与真实节点对应关系
        self.nodes_map = []
        # 真实节点与虚拟节点的字典映射
        self.nodes_replicas = {}
        # 真实节点
        self.nodes = nodes
        # 每个真实节点创建的虚拟节点的个数
        self.replicas = replicas

        if self.nodes:
            for node in self.nodes:
                self._add_nodes_map(node)
            self._sort_nodes()

    def get_node(self, key):
        """ 根据KEY值的hash值，返回对应的节点
        算法是： 返回最早比key_hash大的节点
        """
        key_hash = abs(crc32(key))
        #print '(%s' % key_hash
        for node in self.nodes_map:
            if key_hash > node[0]:
                continue
            return node
        return None

    def add_node(self, node):
        # 添加节点
        self._add_nodes_map(node)
        self._sort_nodes()

    def remove_node(self, node):
        # 删除节点
        if node not in self.nodes_replicas.keys():
            pass
        discard_rep_nodes = self.nodes_replicas[node]
        self.nodes_map = filter(lambda x: x[0] not in discard_rep_nodes, self.nodes_map)

    def _add_nodes_map(self, node):
        # 增加虚拟节点到nodes_map列表
        nodes_reps = []
        for i in xrange(self.replicas):
            rep_node = '%s_%d' % (node, i)
            node_hash = abs(crc32(rep_node))
            self.nodes_map.append((node_hash, node))
            nodes_reps.append(node_hash)
        # 真实节点与虚拟节点的字典映射
        self.nodes_replicas[node] = nodes_reps

    def _sort_nodes(self):
        # 按顺序排列虚拟节点
        self.nodes_map = sorted(self.nodes_map, key=lambda x:x[0])




if __name__ == '__main__':
    # lcs()
    memcache_servers = [
        '127.0.0.1:7001',
        '127.0.0.1:7002',
        '127.0.0.1:7003',
        '127.0.0.1:7004',
    ]

    h = HashConsistency(memcache_servers)

    for k in h.nodes_map:
        print k

    mc_servers_dict = {}
    for ms in memcache_servers:
        mc_servers_dict[ms] = ms

    # 循环10此给memcache 添加key，这里使用了一致性hash，那么key将会根据hash值落点到对应的虚拟节点上
    for i in xrange(10):
        key = 'key_%s' % i
        print key
        server = h.get_node(key)[1]
        mc = mc_servers_dict[server]
        print mc,key
