#!/usr/bin/env python

from __future__ import print_function
from docker_utils import (get_repos, get_teams, get_permissions, get_members, logout, create_repo, create_team, 
                          add_permissions, add_member, delete_repo, delete_team, delete_permissions, delete_member)
from argparse import ArgumentParser
import yaml
import sys
from os.path import join, dirname, abspath

parser = ArgumentParser(description='Synchronize Docker HUB with yaml configuration file')
parser.add_argument('-u', '--username', dest='username', help="Provide Docker Hub username for synchronization", type=str, default='cmsuser')
parser.add_argument('-n', '--dry-run', dest='dryrun', help="Dry Run mode enabled by default. Disable it to make changes to docker hub", action="store_true", default=False)
args = parser.parse_args()
changes_applied = False
if not args.dryrun:
  print('==== DRY RUN MODE DISABLED ====')

def update_dockerhub(config_file, docker_hub, username = args.username, team_name = None, repo = None, 
                     team_id = None, yaml_permissions = None, what_to_sync = None, dryrun=args.dryrun):
  dryrun_message = 'Dry run mode enabled, no changes to Docker Hub applied'
  global changes_applied
  diff_list = [item for item in config_file + docker_hub if item not in config_file or item not in docker_hub]
  for list_item in diff_list:
    if list_item in config_file and list_item not in docker_hub:
      changes_applied = True
      if what_to_sync == 'repos':
        print('###### Adding repository: "%s"' % list_item)
        print(dryrun_message) if dryrun else print(create_repo(username, list_item)[0])   
      elif what_to_sync == 'teams':
        print('###### Creating team: "%s"' % list_item)
        print(dryrun_message) if dryrun else print(create_team(username, list_item)[0])
      elif what_to_sync == 'permissions':
        print('###### Adding "%s" permission to "%s" repository for "%s" team:' % (yaml_permissions[list_item], list_item, team_name))
        print(dryrun_message) if dryrun else print(add_permissions(username, list_item, team_id, yaml_permissions[list_item])[0])
      elif what_to_sync == 'members':
        print('###### Adding member "%s" to "%s" team:' % (list_item, team_name))
        print(dryrun_message) if dryrun else print(add_member(username, team_name, list_item)[0])
    if list_item in docker_hub and list_item not in config_file:
      changes_applied = True
      if what_to_sync == 'repos':
        print('###### Deleting repository: "%s"' % list_item)
        if dryrun: print(dryrun_message)
        else:
          delete_status = delete_repo(username, list_item)
          if not delete_status:
            print('Error: %s repository is not empty. Could not be removed' % list_item)
            sys.exit(1)
          elif not delete_status[0]:
            print(delete_status)
            sys.exit(1)
          else: print(delete_status[0])
      elif what_to_sync == 'teams':
        print('###### Deleting team: "%s"' % list_item)
        if dryrun: print(dryrun_message)
        else:
          delete_status = delete_team(username, list_item)
          if not delete_status:
            print('Error: %s team is not empty. Could not be removed' % list_item)
            sys.exit(1)
          elif not delete_status[0]:
            print(delete_status)
            sys.exit(1)
          else: print(delete_status[0])
      elif what_to_sync == 'permissions':
        print('###### Deleting permission for "%s" repository from "%s" team:' % (list_item, team_name))
        print(dryrun_message) if dryrun else print(delete_permissions(username, list_item, team_id)[0])
      elif what_to_sync == 'members':
        print('###### Deleting member "%s" from "%s" team:' % (list_item, team_name))
        print(dryrun_message) if dryrun else print(delete_member(username, team_name, list_item)[0])
