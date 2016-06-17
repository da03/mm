import sys, argparse, logging, subprocess, os, shutil

from utils import parse_params

def process_args(args):
    parser = argparse.ArgumentParser()

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

def add_machine(app_relative_path, central_server, name, user_name, host_name, public_ip):
    cmd = 'python %s %s %s %s %s'%(os.path.join(app_relative_path, 'add_machine.py'), name, user_name, host_name, public_ip)
    #cmd = 'cat %s >> %s'%(os.path.join(app_relative_dir, 'keys', 'id_rsa.pub.%s'%name), os.path.join(base_ssh_dir, 'authorized_keys'))
    logging.info('ssh %s %s'%(central_server, cmd))
    ret = subprocess.call(["ssh", central_server, cmd])

def remote_add_machine(app_relative_path, central_server, source_name, source_machine, dest_machine, ssh_abs_path):
    cmd = 'scp %s %s:%s'%(central_server+':'+os.path.join(app_relative_path, 'keys/id_rsa.pub.%s'%source_name), dest_machine, os.path.join(app_relative_path, 'keys/'))
    ret = subprocess.call(["ssh", central_server, cmd])
    logging.info('ssh %s %s'%(central_server, cmd))
    pos = source_machine.find('@')
    user_name = source_machine[:pos]
    host_name = source_machine[(pos+1):]
    public_ip = host_name
    cmd = 'ssh %s "python %s %s %s %s %s"'%(dest_machine, os.path.join(app_relative_path, 'add_machine.py'), source_name, user_name, host_name, public_ip)
    logging.info('ssh %s %s'%(central_server, cmd))
    ret = subprocess.call(["ssh", central_server, cmd])

def sync_machine(ssh_relative_path, ssh_abs_path, app_relative_path, app_abs_path, central_server):
    dest_pub_key = os.path.join(app_abs_path, 'id_rsa.pub')
    source_pub_key = "%s:%s"%(central_server,os.path.join(ssh_relative_path, 'id_rsa.pub'))
    logging.info('scp %s %s'%(source_pub_key, dest_pub_key))
    ret = subprocess.call(["scp", source_pub_key, dest_pub_key])
    source_config_file = '%s:'%central_server + os.path.join(app_relative_path, 'config.txt')
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
    mode = args[1] # mcp, mls, mssh
    name = args[0]
   
    if mode == 'mcp':
        source = args[2]
        dest = args[3]
        parameters = process_args(args[4:])
    elif mode == 'mls':
        dest = args[2]
        parameters = process_args('')
    elif mode == 'mssh':
        dest = args[2]
        parameters = process_args('')
    elif mode == 'mcpr':
        source = args[2]
        dest = args[3]
        parameters = process_args(args[4:])
    else:
        assert False, mode

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

    # read config file
    params = parse_params(parameters.config_path)

    # add public key file to central server public key file
    assert 'central' in params, 'central server must be set in config file %s. The required format is \'central: username@machine-ip\''%parameters.config_path

    central_server = params['central']
    logging.info('Central server: %s'%central_server)

    source_pub_key = os.path.join(ssh_abs_path, 'id_rsa.pub')
    dest_pub_key = "%s:%s"%(central_server,os.path.join(os.path.join(app_relative_path, 'keys'), 'id_rsa.pub.%s'%name))
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

    # sync machine file, add central server key file to local authorized_keys
    sync_machine(ssh_relative_path, ssh_abs_path, app_relative_path, app_abs_path, central_server)

    if mode == 'mcp' or mode == 'mcpr':
        pos = source.find(':')
        if pos > 0:
            source_name = source[:pos]
            source_path = source[(pos+1):]
        else:
            source_name = name
            source_path = os.path.realpath(source)
        pos = dest.find(':')
        if pos > 0:
            dest_name = dest[:pos]
            dest_path = dest[(pos+1):]
        else:
            dest_name = name
            dest_path = os.path.realpath(dest)
        params = parse_params(parameters.config_path)
        assert source_name in params, source_name
        assert dest_name in params, dest_name
        source_machine = params[source_name]
        dest_machine = params[dest_name]
        # copy authorized key file
        remote_add_machine(app_relative_path, central_server, source_name, source_machine, dest_machine, ssh_abs_path)

        if mode == 'mcp':
            cmd = 'scp %s %s:%s'%(source_machine+':'+source_path, dest_machine, dest_path)
        else:
            cmd = 'scp -r %s %s:%s'%(source_machine+':'+source_path, dest_machine, dest_path)
        print (cmd)
        ret = subprocess.call(["ssh", central_server, cmd])
    elif mode == 'mls':
        pos = dest.find(':')
        if pos > 0:
            dest_name = dest[:pos]
            dest_path = dest[(pos+1):]
        else:
            dest_name = name
            dest_path = os.path.realpath(dest)
        params = parse_params(parameters.config_path)
        assert dest_name in params, dest_name
        dest_machine = params[dest_name]
        cmd = 'ls -l %s'%(dest_path)
        ret = subprocess.check_output(["ssh", dest_machine, cmd])
        print (ret)
    elif mode == 'mssh':
        dest_name = dest
        params = parse_params(parameters.config_path)
        assert dest_name in params, dest_name
        dest_machine = params[dest_name]
        ret = subprocess.call(["ssh", dest_machine])



if __name__ == "__main__":
    main(sys.argv[1:])
