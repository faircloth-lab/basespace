#!/usr/bin/env python
# encoding: utf-8
"""
File: unnamed_file.py
Author: Brant Faircloth

Created by Brant Faircloth on 26 October 2013 12:10 PDT (-0700)
Copyright (c) 2013 Brant C. Faircloth. All rights reserved.

Description:

"""

import os
import requests
import ConfigParser

import pdb

BASE = 'https://api.basespace.illumina.com'
VER = 'v1pre3'

class BaseSpaceUser(object):
    def __init__(self, json):
        for name, value in json.items():
            setattr(self, name.lower(), value)

    def __str__(self):
        return "Name={} id={}".format(
            self.name,
            self.id
        )

    def __repr__(self):
        return "<Name={} id={}>".format(
            self.name,
            self.id
        )


class BaseSpaceRuns(object):
    def __init__(self, json):
        for name, value in json.items():
            if name == 'UserOwnedBy':
                self.owner = BaseSpaceUser(value)
            if name == 'UserUploadedBy':
                self.uploaded = BaseSpaceUser(value)
            else:
                setattr(self, name.lower(), value)

    def __str__(self):
        return "Experiment={} id={}".format(self.name, self.id)

    def __repr__(self):
        return "<Experiment={} id={}>".format(
            self.experimentname,
            self.id
        )


class BaseSpaceSamples(object):
    def __init__(self, json):
        for name, value in json.items():
            if name == 'UserOwnedBy':
                self.owner = BaseSpaceUser(value)
            if name == 'UserUploadedBy':
                self.uploaded = BaseSpaceUser(value)
            else:
                setattr(self, name.lower(), value)

    def __str__(self):
        return "Name={} id={}".format(self.name, self.id)

    def __repr__(self):
        return "<Name={} id={}>".format(
            self.name,
            self.id
        )


class BaseSpaceSampleFiles(object):
    def __init__(self, json):
        for name, value in json.items():
            setattr(self, name.lower(), value)

    def __str__(self):
        return "Name={} id={}".format(self.name, self.id)

    def __repr__(self):
        return "<Name={} id={}>".format(
            self.name,
            self.id
        )


class BaseSpace(object):
    def __init__(self, credentials):
        self.base_url = "{}/{}".format(BASE, VER)
        conf = ConfigParser.ConfigParser()
        conf.optionxform = str
        conf.read(credentials)
        self.id = conf.get('credentials', 'id')
        self.secret = conf.get('credentials', 'secret')
        try:
            self.token = {'access_token':conf.get('credentials', 'token')}
        except:
            pass
        self._check_login()

    def _check_login(self, silent = False):
        r = requests.get("{}/users/current".format(self.base_url), params=self.token)
        if r.status_code == 200:
            json = r.json()
            self.user = BaseSpaceUser(json['Response'])
            if not silent:
                print "User {}, Id {} logged in.".format(
                    self.user.name,
                    self.user.id
                )

    def runs(self, offset=0, limit=1024, sort='id', asc=True):
        runs = []
        if asc == True:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Asc'}
        else:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Desc'}
        params.update(self.token)
        r = requests.get("{}/users/current/runs".format(self.base_url), params=params)
        if r.status_code == 200:
            json = r.json()
            for item in json['Response']['Items']:
                runs.append(BaseSpaceRuns(item))
        return runs

    def run(self, id, offset=0, limit=1024, sort='id', asc=True):
        if asc == True:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Asc'}
        else:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Desc'}
        params.update(self.token)
        r = requests.get("{}/runs/{}".format(self.base_url, id), params=params)
        if r.status_code == 200:
            json = r.json()
            return BaseSpaceRuns(json['Response'])
        else:
            return None

    def samples(self, obj, offset=0, limit=1024, sort='id', asc=True):
        samples = []
        if asc == True:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Asc'}
        else:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Desc'}
        params.update(self.token)
        pdb.set_trace()
        if isinstance(obj, int):
            r = requests.get("{}/runs/{}/samples".format(self.base_url, obj), params=params)
        else:
            r = requests.get("{}/runs/{}/samples".format(self.base_url, obj.id), params=params)
        if r.status_code == 200:
            json = r.json()
            for item in json['Response']['Items']:
                samples.append(BaseSpaceSamples(item))
        else:
            print r.status_code
        return samples

    def sample_files(self, id, offset=0, limit=1024, sort='id', asc=True):
        files = []
        if asc == True:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Asc'}
        else:
            params = {'Offset':offset, 'Limit':limit, 'SortBy':sort, 'SortDir':'Desc'}
        params.update(self.token)
        pdb.set_trace()
        r = requests.get("{}/samples/{}/files".format(self.base_url, id), params=params)
        if r.status_code == 200:
            json = r.json()
            for item in json['Response']['Items']:
                files.append(BaseSpaceSamples(item))
        else:
            print r.status_code
        return files

    def get_file(self, file):
        name = os.path.basename(file.path)
        with open(name, 'wb') as handle:
            request = requests.get("{}/files/{}/content".format(self.base_url, file.id), params=self.token, stream=True)
            content = 0
            for block in request.iter_content(1024):
                status = r"%10d  [%3.2f%%]" % (content, content * 100. / file.size)
                status = status + chr(8)*(len(status)+1)
                print status
                if not block:
                    break
                handle.write(block)
                content += 1024

