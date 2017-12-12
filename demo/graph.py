# coding=utf-8

def check_cycle_node(node, path):
    """
    计算所有可能路径
    :param node:
    :param path:
    :return:
    """
    if node.has_post():
        if node in path:
            return True
        else:
            path.append(node)
    if node.has_next():
        post_nodes = node.next()
        for _node in post_nodes:
            extend_path = []
            extend_path.extend(path)
            if check_cycle_node(_node,extend_path):
                return True
    return False


class DAG():
    def __init__(self, root):
        self.root = root

    def check_cycle(self):
        """
        判断是否存在回环
        :return:
        """
        # 即有前置节点又有后置节点
        path = []
        return check_cycle_node(self.root, path)


class Node(object):
    def __init__(self, data):
        self.pre = []
        self.post = []
        self.data = data

    def add_relation(self, pre_node=None, post_node=None):
        # setattr(self, 'pre', pre)
        if pre_node not in self.pre:
            self.pre.append(pre_node)
        if post_node not in self.post:
            self.post.append(post_node)

    def __eq__(self, other):
        """
        通过data来判断是否是相同元素
        :param other:
        :return:
        """
        if self.data == other.data:
            return True
        else:
            return False

    def has_post(self):
        """
        判断节点是否存在后置节点
        :return:
        """
        return len(self.post) > 0

    def has_next(self):
        return len(self.post) > 0

    def next(self):
        return self.post


if __name__ == '__main__':
    n0 = Node('0')
    n1 = Node('1')
    n2 = Node('2')
    n3 = Node('3')
    n4 = Node('4')
    n5 = Node('5')
    n6 = Node('6')
    n7 = Node('7')
    n8 = Node('8')
    n9 = Node('9')
    n10 = Node('10')
    n11 = Node('11')
    n0.add_relation(post_node=n1)
    n1.add_relation(post_node=n2)
    n1.add_relation(post_node=n3)
    n2.add_relation(post_node=n8)
    n3.add_relation(post_node=n4)
    n3.add_relation(post_node=n5)
    n3.add_relation(post_node=n6)
    n4.add_relation(post_node=n7)
    n5.add_relation(post_node=n7)
    n6.add_relation(post_node=n7)
    n7.add_relation(post_node=n9)
    n8.add_relation(post_node=n9)
    n9.add_relation(post_node=n10)
    n10.add_relation(post_node=n11)
    n7.add_relation(post_node=n3)
    dag = DAG(n0)
    print dag.check_cycle()
