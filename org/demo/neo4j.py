# coding=utf-8
import json
import os
import random
import logging
import uuid
import gevent

from py2neo import authenticate, Graph, Relationship
from gevent import monkey;

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#                     datefmt='%m-%d %H:%M',
#                     filename='test.log',
#                     filemode='w')
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# # 设置日志打印格式
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# console.setFormatter(formatter)
# # 将定义好的console日志handler添加到root logger
# logging.getLogger('').addHandler(console)
# 定义一个Handler打印INFO及以上级别的日志到sys.stderr
# merge (a:Person {name:'lilly',age:18}) merge (b:Person {name:'jetty',age:18}) create (a)-[:friend]->(b)
# MATCH (user:User { name: 'Adam' })-[:FRIEND *..2]-(friend) RETURN friend
# match (n) detach delete n
logging.basicConfig(
    level=logging.WARN,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)
monkey.patch_all()

class Neo4j():
    def __init__(self):
        self.graph = None

    def auth(self):
        authenticate("localhost:7474", "neo4j", "admin")
        self.graph = Graph()

    def eval(self, statement, parameters=None):
        return self.graph.cypher.execute(statement, parameters)

    def find(self, label, property_key=None, property_value=None, limit=None):
        return self.graph.find(label, property_key, property_value, limit)

    def merge(self, label, property_key=None, property_value=None, limit=None):
        return self.graph.merge(label, property_key, property_value, limit)

    def match(self, start_node=None, rel_type=None, end_node=None, bidirectional=False, limit=None):
        """
        For example, to find all of Alice’s friends:

        for rel in graph.match(start_node=alice, rel_type="FRIEND"):
            print(rel.end_node.properties["name"])
        Parameters:
        start_node – bound start Node to match or None if any
        rel_type – type of relationships to match or None if any
        end_node – bound end Node to match or None if any
        bidirectional – True if reversed relationships should also be included
        limit – maximum number of relationships to match or None if no limit
        Returns:
        matching relationships
        Return type:
        generator
        """
        return self.graph(start_node, rel_type, end_node, bidirectional, limit)


def random_str():
    # ''.join(random.sample(string.ascii_letters+string.digits, 8))
    return ''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(8)))


if __name__ == '__main__':
    neo = Neo4j()
    neo.auth()
    neo.eval('create constraint on (n:Person) assert n.gid is unique')
    # neo.eval('drop constraint on (n:Person) assert n.gid is unique')
    neo.eval('CREATE INDEX ON :Person(phone)')
    neo.eval('CREATE INDEX ON :Person(qq)')
    for x in xrange(10000000):
        phone = random.randint(13899999999, 13999999999)
        qq = random.randint(89999999, 99999999)
        gid = str(uuid.uuid1())
        gender = ['M', 'W'].pop(random.randint(0, 1))
        interest = [u'阅读', u'游泳', u'篮球', u'跑步', u'游戏', u'睡觉', u'唱歌', u'跳舞', u'打牌', u'画画'][
                   random.randint(-10, 10):random.randint(-10, 10)]
        dic = {'phone': phone, 'qq': qq, 'gid': gid, 'gender': gender, 'interest': interest}
        statement = 'merge (a:Person {gid:$gid}) on create set a.phone = $phone,a.qq = $qq,a.gender = $gender,' \
                    'a.interest = $interest,a.created = timestamp() on match set a.gid=$gid ' \
                    'with a ' \
                    'match (b:Person {phone:$phone}) ' \
                    'with a,b where b.gid <> $gid ' \
                    'merge (a)-[:phone]->(b) ' \
                    'with a ' \
                    'match (b:Person {qq:$qq}) ' \
                    'with a,b where b.gid <> $gid ' \
                    'merge (a)-[:qq]->(b)'
        logger.warn(json.dumps(dic))
        print statement
        neo.eval(statement, dic)
