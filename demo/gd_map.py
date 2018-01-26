# coding=utf-8
import requests

r=requests.get('http://restapi.amap.com/v3/place/around?key=3e8b6ff4cd8f087b81f4e45aa9288c3c&location=116.481488,39.990464&keywords=肯德基&types=050301&offset=20&page=1&extensions=all')
print r.text
