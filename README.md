# ansible-ovh
OVH API Ansible module

### Description
This module provisions an OVH dedicated server.
Install a dedicated server using an existing template.

This module is *not being actively developed* at the moment.
Contributions are welcome.

**NOTE** that this module will install a new or existing server! take care when selecting server

### Requirements
OVH Configuration to be passed as a variable - 'config_file'. yaml file containing the following:
```
endpoint: ovh-ca
application_key: somekey
application_secret: somesecret
consumer_key: someconsumerkey
```

### Available options:
```
options:
    service:
        description:
            - OVH Service name

    template:
        description:
            - Template name to use for the installation [must exist under /me/templates]
        required: true

    hostname:
        description:
            - Hostname
        required: false

    ssh_key:
        description:
            - SSH Key to use for login
        required: false

    distrib_kernel:
        description:
            - Use distribution kernel instead of OVH's kernel
        required: false
```

### Example Playbook:
```
---
- hosts: localhost
  tasks:
    - name: Install dedicated server
      ovh_server:
        service: name
        template: foo
        hostname: bar
        ssh_key: pub
        distrib_kernel: true
      with_items:
        - { name: 'server1', hostname: 'servername' }
        - { name: 'server2', hostname: 'servername' }
```
