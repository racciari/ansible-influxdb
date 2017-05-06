# ansible-influxdb

Ansible module and plugin to send data to InfluxDB

## Introduction

This repository provides an Ansible module to send messages to an InfluxDB database. It also contain an Ansible callback that log ansible command result to InfluxDB.

## InfluxDB module

To use this module, you can declare it like this to access the `inventory_hostname` variable and tune your message.  
You can add any tag you want to the `tags` parameter.  

```
---
- hosts: myhostgroup
  tasks:
    - influxdb:
        uri: http://localhost:8086/write?u=root&p=root&db=graphite
        measurement: events
        tags:
          host: "{{ inventory_hostname }}"
          title: "title message"
        value: "Log message for host {{ inventory_hostname }}"
      delegate_to: localhost
```

## InfluxDB callback

To use the callback, you need to enable it in your `/etc/ansible/ansible.cfg`. In the `[defaults]` section, you must configure the following:

```
callback_whitelist = influxdb
bin_ansible_callbacks = True
callback_plugins = /path/to/callback/
```

For the callback to work, you need to export at least the following environment variable:

```
export INFLUXDB_URI='http://prod.scalair.openio.io:8086/write?u=root&p=root&db=graphite'
```
