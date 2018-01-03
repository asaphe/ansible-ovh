#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ovh_server

short_description: ovh api /server

version_added: "2.4"

description:
    - "This module provisions an OVH dedicated server"

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

    reinstall:
        description:
            - Reinstall the OS
        required: false

extends_documentation_fragment:
    - ovh

author:
    - Asaph Efrati (@asaphe)
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
    reinstall: false
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
import yaml
try:
    import ovh
    import ovh.exceptions
    from ovh.exceptions import APIError
except ImportError:
    module.fail_json(msg='missing a required module', **result)


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
    results = client.get('/me/installationTemplate')
    return results


def install_dedicated_server(client, service, data):
    """Install a dedicated server from a Template."""
    client.post('/dedicated/server/%s/install/start' %
                service,
                **data)


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        service=dict(type='str', required=True),
        template=dict(type='str', required=True),
        hostname=dict(type='str', required=False),
        ssh_key=dict(type='str', required=False),
        distrib_kernel=dict(type='bool', required=False, default=False),
        reinstall=dict(type='bool', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        cfg = load_yaml('./ovh.yaml')
        client = ovh_client(**cfg)
        server = client.get('/dedicated/server/%s' % module.params['service'])
        if not server.get('os') and module.params['reinstall']:
            templates = get_templates(client)
            if module.params['template'] in templates:
                data = {"details": {"language": "en",
                                    "customHostname": module.params['hostname'],
                                    "sshKeyName": module.params['ssh_key'],
                                    "useDistribKernel": module.params['distrib_kernel']
                                    },
                                    "templateName": module.params['template']}
                install_dedicated_server(client, module.params['service'], data)
    except APIError as api_error:
        module.fail_json(msg=str(api_error), **result)
    except IOError as e:
        module.fail_json(msg=str(e), **result)
    except Exception as e:
        module.fail_json(msg=str(e), **result)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    # result['original_message'] = module.params['hostname']
    # result['message'] = 'goodbye'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['hostname']:
    #     result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params['hostname'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
