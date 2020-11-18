#!/usr/bin/env python

from __future__ import print_function
from json import loads
from os.path import dirname, abspath, join, expanduser
from requests import request
from requests.exceptions import HTTPError
import os, glob

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

def get_tags(image, page_size=500):
  uri = '/repositories/%s/tags' % image
  payload = {"page_size" : page_size}
  response = hub_request(uri, params=payload, json=True)
  tags = []
  try:
    for tag in response['results']:
      tags.append(str(tag['name']))
  except: return (False, response)
  return (True, tags)

def get_repos(username, page_size=500):
  uri = '/repositories/%s/' % username
  payload = {"page_size" : page_size}
  response = hub_request(uri, params=payload, json=True)
  repos = []
  try:
    for repo in response['results']:
      repos.append(str(repo['name']))
  except: return (False, response)
  return (True, repos)

def create_repo(username, repo, private=False):
  payload = {
    "namespace":"%s" % username,
    "name":"%s" % repo,
    "is_private":"%s" % private
  }
  response = hub_request("/repositories/", payload, method = 'POST')
  return (False, response, response.reason, response.text) if not response.ok else (response.ok,)

def delete_repo(username, repo, force=False):
  uri = '/repositories/%s/%s' % (username, repo)
  if force or not get_tags('%s/%s'%(username,repo))[1]:
    response = hub_request(uri, method = 'DELETE')
    return (False, response, response.reason, response.text) if not response.ok else (response.ok,)
  else: return False
