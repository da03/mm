import sys, argparse, logging, subprocess, os, shutil

from utils import parse_params

def process_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--name', dest="name",
                        type=str, required=True,
                        help=('Name of the machine. You can use any nickname '
                            'as long as it is not used by other machines.' 
                        ))
    parser.add_argument('--log-path', dest="log_path",
                        type=str, default='log.txt',
                        help=('Log file path, default=log.txt' 
                        ))
    parser.add_argument('--config-path', dest="config_path",
                        type=str, default='config.txt',
                        help=('Config file path, default=config.txt' 
                        ))
    parameters = parser.parse_args(args)
    return parameters

def set_alias(home_abs_path, app_abs_path, name):
    bashrc_path = os.path.join(home_abs_path, '.bashrc')
    tmp_bashrc_path = os.path.join(home_abs_path, '.bashrc.tmp')
    # create .bashrc if not present
    if not os.path.isfile(bashrc_path):
        f = open(bashrc_path, 'w')
        f.close()

    # add to authorized_keys
    with open(bashrc_path) as fin:
        with open(tmp_bashrc_path, 'w') as fout:
            for line in fin:
                if 'alias mcp' in line or 'alias mls' in line or 'alias mssh' in line or 'alias mcpr' in line:
                    continue
                fout.write(line)
            fout.write('alias mcp=\'python %s %s mcp\'\n'%(os.path.join(app_abs_path, 'run.py'), name))
            fout.write('alias mcpr=\'python %s %s mcpr\'\n'%(os.path.join(app_abs_path, 'run.py'), name))
            fout.write('alias mls=\'python %s %s mls\'\n'%(os.path.join(app_abs_path, 'run.py'), name))
            fout.write('alias mssh=\'python %s %s mssh\'\n'%(os.path.join(app_abs_path, 'run.py'), name))
        shutil.move(tmp_bashrc_path, bashrc_path)
    #ret = subprocess.call("source %s"%bashrc_path, shell=True)
    #ret = subprocess.call('alias mcp=\'python %s mcp\'\n'%(os.path.join(app_abs_path, 'run.py')), shell=True)
    #fout.write('alias mls=\'python %s mls\'\n'%(os.path.join(app_abs_path, 'run.py')))
    #fout.write('alias mssh=\'python %s mssh\'\n'%(os.path.join(app_abs_path, 'run.py')))

def add_machine(app_relative_path, central_server, name, user_name, host_name, public_ip):
    cmd = 'python %s %s %s %s %s'%(os.path.join(app_relative_path, 'add_machine.py'), name, user_name, host_name, public_ip)
    #cmd = 'cat %s >> %s'%(os.path.join(app_relative_dir, 'keys', 'id_rsa.pub.%s'%name), os.path.join(base_ssh_dir, 'authorized_keys'))
    print ('ssh %s %s'%(central_server, cmd))
    logging.info('ssh %s %s'%(central_server, cmd))
    ret = subprocess.call(["ssh", central_server, cmd])

def sync_machine(ssh_relative_path, ssh_abs_path, app_relative_path, app_abs_path, central_server):
    dest_pub_key = os.path.join(app_abs_path, 'id_rsa.pub')
    source_pub_key = "%s:%s"%(central_server,os.path.join(ssh_relative_path, 'id_rsa.pub'))
    print ('scp %s %s'%(source_pub_key, dest_pub_key))
    logging.info('scp %s %s'%(source_pub_key, dest_pub_key))
    ret = subprocess.call(["scp", source_pub_key, dest_pub_key])
    source_config_file = '%s:'%central_server+os.path.join(app_relative_path, 'config.txt')
    dest_config_file = os.path.join(app_abs_path, 'config.txt')
    ret = subprocess.call(["scp", source_config_file, dest_config_file])
    # copy public key file
    authorized_keys_path = os.path.join(ssh_abs_path, 'authorized_keys')
    tmp_authorized_keys_path = os.path.join(ssh_abs_path, 'authorized_keys.tmp')
    # create authorized_keys if not present
    if not os.path.isfile(authorized_keys_path):
        f = open(authorized_keys_path, 'w')
        f.close()

    # add to authorized_keys
    with open(authorized_keys_path) as fin:
        with open(tmp_authorized_keys_path, 'w') as fout:
            for line in fin:
                if central_server in line:
                    continue
                fout.write(line)
            fout.write(open(dest_pub_key).readline())
    shutil.move(tmp_authorized_keys_path, authorized_keys_path)
    os.chmod(authorized_keys_path, 0600)

def main(args):
    if not os.path.isdir('keys'):
        os.mkdir('keys')
    parameters = process_args(args)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s',
        filename=parameters.log_path)

    # figure out paths
    home_abs_path = os.path.expanduser('~')
    app_abs_path = os.path.dirname(os.path.realpath(__file__))
    app_relative_path = app_abs_path.replace(home_abs_path, '~')
    logging.info('Application base directory: %s.' %app_relative_path)

    ssh_relative_path = '~/.ssh'
    ssh_abs_path = ssh_relative_path.replace('~', home_abs_path)

    name = parameters.name
    # read config file
    params = parse_params(parameters.config_path)

    # add public key file to central server public key file
    assert 'central' in params, 'central server must be set in config file %s. The required format is \'central: username@machine-ip\''%parameters.config_path

    central_server = params['central']
    logging.info('Central server: %s'%central_server)

    source_pub_key = os.path.join(ssh_abs_path, 'id_rsa.pub')
    dest_pub_key = "%s:%s"%(central_server,os.path.join(os.path.join(app_relative_path, 'keys'), 'id_rsa.pub.%s'%name))
    print ('scp %s %s'%(source_pub_key, dest_pub_key))
    logging.info('scp %s %s'%(source_pub_key, dest_pub_key))
    # copy public key file
    ret = subprocess.call(["scp", source_pub_key, dest_pub_key])

    # get hostname
    host_name = subprocess.check_output(["hostname"])
    assert host_name, 'hostname command fails!'
    host_name = host_name.strip()
    # get username
    user_name = subprocess.check_output(["whoami"])
    assert user_name, 'whoami command fails!'
    user_name = user_name.strip()
    # get public ip
    public_ip = subprocess.check_output("wget http://ipinfo.io/ip -qO -", shell=True)
    assert public_ip, 'wget command fails!'
    public_ip = public_ip.strip()
    # add to authorized keys
    add_machine(app_relative_path, central_server, name, user_name, host_name, public_ip)

    logging.info('Key file added to central server.')

    source_pub_key = os.path.join(ssh_abs_path, 'id_rsa.pub')
    dest_pub_key = os.path.join(os.path.join(app_abs_path, 'keys'), 'id_rsa.pub.%s'%name)
    shutil.copy(source_pub_key, dest_pub_key)
    cmd = 'python %s %s %s %s %s'%(os.path.join(app_abs_path, 'add_machine.py'), name, user_name, host_name, public_ip)
    subprocess.call(cmd, shell=True)

    # sync machine file, add central server key file to local authorized_keys
    sync_machine(ssh_relative_path, ssh_abs_path, app_relative_path, app_abs_path, central_server)

    # set alias
    set_alias(home_abs_path, app_abs_path, name)
if __name__ == "__main__":
    main(sys.argv[1:])
