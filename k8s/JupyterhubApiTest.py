#!/usr/bin/python3
# -*- coding: utf-8 -*-


if __name__ == '__main__':
    import requests

    token = '40d051d3a8ce470ba6adbc1a05bd027a'
    api_url = 'http://192.168.163.110:8000/hub/api'
    r = requests.get(api_url + '/users',
                     headers={
                         'Authorization': 'token %s' % token,
                     }
                     )

    r.raise_for_status()
    users = r.json()
    print(users)