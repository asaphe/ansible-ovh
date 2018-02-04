#!/usr/bin/python
# Copyright (c) 2017 [https://github.com/asaphe,https://github.com/rafi]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
---
module: ovh_server
short_description: Install a dedicated server using a template.
version_added: "2.4"
description:
    - This module provisions an OVH dedicated server using a template.
    - Requires a config file with OVH Credentials or ENV variables.
options:
  config_file:
    required: False
    description:
      - a yaml file containing OVH (endpoint, application_key, application_secret, consumer_key)
        which is required for OVH api calls.
      - if no file has been provided ENV variables will be used.
  service:
    required: True
    description:
      - Service name as per OVH allocation
  template:
    required: False
    description:
      - Template name to use for the installation [must exist under
        /me/templates].
  hostname:
    required: False
    description:
      - Server hostname to set.
  ssh_key:
    required: False
    description:
      - SSH Key defined in OVH to use for login.
  distrib_kernel:
    required: False
    default: False
    description:
      - Distribution kernel [OVH/dist].
  installation_status:
    required: False
    default: False
    description:
      - Determines if the module will return the
        installation status
  install_server:
    required: False
    default: False
    description:
      - Determines if the module will install
        selected servers
requirements:
    - "python >= 2.6"
authors:
    - "Asaph Efrati (@asaphe)"
    - "Rafael Bodill (@rafi)"
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  ovh_server:
    service: name
    template: foo
    hostname: bar
    ssh_key: pub
    distrib_kernel: true
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
import json
import yaml
import os
try:
    import ovh
    import ovh.exceptions
    from ovh.exceptions import APIError
except ImportError:
    raise ImportError('missing a required module')


def ovh_client(endpoint, application_key, application_secret, consumer_key):
    """Create a client connection to OVH."""
    if (v is not None for v in [endpoint,
                                application_key,
                                application_secret,
                                consumer_key]):
        return ovh.Client(
            endpoint=endpoint,
            application_key=application_key,
            application_secret=application_secret,
            consumer_key=consumer_key)
    else:
        raise Exception('Variable set to None. cannot be None.')


def ovh_client_env():
    """Load environment variables and return a client to OVH Endpoint."""
    endpoint = os.environ.get('endpoint', 'ovh-ca')
    application_key = os.environ.get('application_key')
    application_secret = os.environ.get('application_secret')
    consumer_key = os.environ.get('consumer_key')
    if (v is not None for v in [endpoint,
                                application_key,
                                application_secret,
                                consumer_key]):
        return ovh.Client(
            endpoint=endpoint,
            application_key=application_key,
            application_secret=application_secret,
            consumer_key=consumer_key)
    else:
        raise Exception('Variable set to None. cannot be None.')


def load_yaml(config_file):
    """Load the configuration file."""
    with open(config_file, 'r') as yml_file:
        cfg = yaml.load(yml_file)
    return cfg


def get_dedicated_server(client, service):
    """Get a dedicated server."""
    return client.get('/dedicated/server/%s' % service)


def get_templates(client):
    """Get a list of available templates."""
    return client.get('/me/installationTemplate')


def install_dedicated_server(client, service, data):
    """Install a dedicated server from a Template."""
    client.post('/dedicated/server/%s/install/start' %
                service,
                **data)


def get_installation_status(client, service):
    """Get installation status."""
    try:
        return client.get('/dedicated/server/%s/install/status' % service)
    except APIError as api_error:
        return api_error


def run_module():
    """Run the module."""
    module_args = dict(
        service=dict(type='str', required=True),
        template=dict(type='str', required=False),
        hostname=dict(type='str', required=False),
        ssh_key=dict(type='str', required=False),
        distrib_kernel=dict(type='bool', required=False, default=False),
        config_file=dict(type='str', required=False),
        installation_status=dict(type='bool', required=False, default=False),
        install_server=dict(type='bool', required=False, default=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        cfg = load_yaml(module.params['config_file'])
        if not cfg:
            cfg = ovh_client_env
        client = ovh_client(**cfg)
        templates = get_templates(client)
        if module.params['template'] in templates:
            data = {"details": {"language": "en",
                                "customHostname": module.params['hostname'],
                                "sshKeyName": module.params['ssh_key'],
                                "useDistribKernel": module.params['distrib_kernel']
                                },
                    "templateName": module.params['template']}
        if module.params['install_server']:
            install_dedicated_server(client, module.params['service'], data)
        if module.params['installation_status']:
            results = get_installation_status(client,
                                             module.params['service'])
            if 'Server is not being installed or reinstalled at the moment' in results[0]:
                result['original_message'] = results[0]
                result['message'] = 'API Error has occured %s' % module.params['service']
                result['changed'] = False
    except APIError as api_error:
        module.fail_json(msg=str(api_error), **result)
    except IOError as e:
        module.fail_json(msg=str(e), **result)
    except Exception as e:
        module.fail_json(msg=str(e), **result)

    if module.check_mode:
        return result

    module.exit_json(**result)


def main():
    """Run main."""
    run_module()


if __name__ == '__main__':
    main()
