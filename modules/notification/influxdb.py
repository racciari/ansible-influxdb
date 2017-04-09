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

# For Ansible 2.2
# ANSIBLE_METADATA = {'metadata_version': '1.0',
#                     'status': ['stableinterface'],
#                     'supported_by': 'curated'}

DOCUMENTATION = """
---
author: "Romain Acciari"
module: influxdb
short_description: Write to InfluxDB
description:
  - This module is useful for sending data to InfluxDB from playbooks.
version_added: "0.1"
options:
    uri:
        description:
        - URI of the InfluxDB database.
        required: true
    database:
        description:
        - Database to use.
        default: graphite
        required: true
    precision:
        description:
        - The precision to store data
        default: events
        required: false
    measurement:
        description:
        - Measurement to store data.
        default: events
        required: false
    tags:
        description:
        - Tags to apply.
        required: false
    value:
        description:
        - Value to store.
        required: true
    epoch:
        description:
        - Epoch time to show value.
        default: current
        required: false
"""

EXAMPLES = """
# Send message "Ansible test" to the events measurement in graphite database
# Tagged with a specified hostname
---
- hosts: localhost
  tasks:
    - influxdb:
        uri: http://127.0.0.1:8086/write
        tags:
          host: myhostname
        value: Ansible test

# Send a message from localhost refering to an Ansible group from the
# inventory. Message customized with targeted hostname
---
- hosts: ansible_group
  tasks:
    - influxdb:
        uri: http://127.0.0.1:8086/write
        database: graphite
        measurement: events
        tags:
          host: "{{ inventory_hostname }}"
        value: Ansible test on {{ inventory_hostname }}
      delegate_to: localhost
"""

import requests
import time
from ast import literal_eval

from ansible.module_utils.basic import AnsibleModule


def main():

    module = AnsibleModule(
        argument_spec=dict(
            uri=dict(default=None),
            database=dict(default='graphite'),
            precision=dict(default='s'),
            measurement=dict(default='events'),
            tags=dict(default=None),
            value=dict(default=None),
            epoch=dict(default=int(time.time()))
        )
    )

    uri = module.params.get('uri')
    database = module.params.get('database')
    precision = module.params.get('precision')
    measurement = module.params.get('measurement')
    tags = module.params.get('tags')
    value = module.params.get('value')
    epoch = module.params.get('epoch')

    # Prepare headers and parameters for Request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'db': database, 'precision': precision}

    # Start building message
    data = '%s,' % measurement
    if tags:
        for k, v in literal_eval(tags).iteritems():
            data += '%s=%s,' % (k, str(v).replace(' ', '\ '))
        data = data[:-1] if data.endswith(',') else data

    data += ' value="%s" %s' % (value, str(epoch).replace(' ', '\ '))

    # Write data to InfluxDB using Request
    try:
        r = requests.Request('POST', uri, headers=headers,
                             data=data, params=params)
        prepared = r.prepare()
        s = requests.Session()
        s.send(prepared)
    except Exception, e:
        module.fail_json(rc=1, msg='Failed to send data to InfluxDB %s: %s'
                         % (uri, e))

    module.exit_json(changed=True, data=data)


main()
