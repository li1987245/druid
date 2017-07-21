# coding=utf-8
from py2neo import authenticate, Graph, NodeSelector

# set up authentication parameters
authenticate("localhost:7474", "neo4j", "admin")
graph = Graph()
selector = NodeSelector(graph)
selected = selector.select("Person",name='tom')
print list(selected)