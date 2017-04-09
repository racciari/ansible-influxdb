# -*- coding: utf-8 -*-
# Copyright 2017 Romain Acciari <romain.acciari@openio.io>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import requests
import time

from ansible.utils.unicode import to_bytes
from ansible.plugins.callback import CallbackBase



class CallbackModule(CallbackBase):
    """
    This Ansible callback plugin to send command lines to an InfluxDB database
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'influxdb'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):

        self.disabled = False

        super(CallbackModule, self).__init__()

        self.influxdb_uri = os.getenv('INFLUXDB_URI')
        self.db = os.getenv('INFLUXDB_DB', 'graphite')
        self.measurement = os.getenv('INFLUXDB_MEASUREMENT', 'events')
        self.precision = os.getenv('INFLUXDB_PRECISION', 's')

        if self.influxdb_uri is None:
            self.disabled = True
            self._display.warning('InfluxDB URI was not provided. The InfluxDB '
                                  'URI can be provided using the `INFLUXDB_URI`'
                                  ' environment variable.')

        self.printed_playbook = False
        self.playbook_name = None
        self.play = None

    def influx(self, tags, message):
        epoch = int(time.time())
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {'db': self.db,'precision': self.precision}

        data = '%s,' % self.measurement
        for k,v in tags.iteritems():
            data += '%s=%s,' % (k, str(v).replace(' ','\ '))
        data = data[:-1] if data.endswith(',') else data
        data += ' value="%s" %s' % (message, str(epoch).replace(' ','\ '))

        r = requests.Request('POST', self.influxdb_uri, headers=headers, data=data, params=params)
        prepared = r.prepare()
        s = requests.Session()
        resp = s.send(prepared)


    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        try:
            command = result._result['cmd']
            res_msg = result._result['stdout']
        except KeyError:
            return
        status = 'OK'
        title = '%s: %s' % (status, command)
        message = '%s<br>\n%s' % (command, res_msg)
        tags = {'host': host, 'command': command, 'title': title, 'status': status}
        self.influx(tags, message)
#        print(json.dumps(result, indent=4, sort_keys=True, default=lambda o: o.__dict__))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        try:
            command = result._result['cmd']
            res_msg = result._result['stdout']
        except KeyError:
            return
        status = 'FAILED'
        title = '%s: %s' % (status, command)
        message = '%s<br>\n%s: %s' % (command, status, res_msg)
        tags = {'host': host, 'command': command, 'title': title, 'status': status}
        self.influx(tags, message)

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        command = result._task._attributes['args']['_raw_params']
        res_msg = result._result['msg']
        status = 'UNREACHABLE'
        title = '%s: %s' % (status, command)
        message = '%s<br>\n%s: %s' % (command, status, res_msg)
        tags = {'host': host, 'command': command, 'title': title, 'status': status}
        self.influx(tags, message)

