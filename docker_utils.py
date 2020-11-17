#!/usr/bin/env python

from __future__ import print_function
from json import loads
from os.path import dirname, abspath, join, expanduser

DOCKER_REGISTRY_API='https://registry-1.docker.io/v2'
DOCKER_HUB_API='https://hub.docker.com/v2'
DOCKER_HUB_TOKEN = None
DOCKER_IMAGE_CACHE = {}

def hub_request(uri, data=None, params=None, headers=None, method='GET', json=False):
  global DOCKER_HUB_TOKEN
  if not DOCKER_HUB_TOKEN:
    DOCKER_HUB_TOKEN = get_token()
  if not headers: headers = {}
  headers['Authorization'] = 'JWT %s' % DOCKER_HUB_TOKEN
  return http_request('%s%s' %(DOCKER_HUB_API, uri), data, params, headers, method, json)

def http_request(url, data=None, params=None, headers=None, method = 'GET', json=False):
  response = request(method=method, url=url, data=data,  params=params, headers=headers)
  return response.json() if json else response

# get token for docker Registry API
def get_registry_token(repo):
  uri = 'https://auth.docker.io/token'
  payload = {
    'service' : 'registry.docker.io',
    'scope' : 'repository:%s:pull' % repo
  }
  return http_request(uri, params = payload, json = True)['token']

# get token for Docker HUB API:
def get_token(filepath=expanduser("~/.docker-token")):
  uri = '%s/users/login/' % DOCKER_HUB_API
  secret = open(filepath).read().strip()
  response = http_request(uri, loads(secret), method = 'POST', json=True)
  try: return response['token']
  except: return response
