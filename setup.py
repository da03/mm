import sys, argparse, logging, subprocess, os

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

def main(args):
    parameters = process_args(args)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s',
        filename=parameters.log_path)

    home_dir = os.path.expanduser('~')
    app_dir = os.path.dirname(os.path.realpath(__file__))
    app_relative_dir = app_dir.replace(home_dir, '~')
    logging.info('Application base directory: %s.' %app_relative_dir)
    base_ssh_dir = '~/.ssh'
    name = parameters.name
    base_ssh_dir_abs = base_ssh_dir.replace('~',os.path.expanduser('~'))
    name = parameters.name
    # read config file
    params = parse_params(parameters.config_path)
    # add public key file to central server public key file
    assert 'central' in params, 'central server must be set in config file %s. The required format is \'central: username@machine-ip\''%parameters.config_path

    central_server = params['central']
    logging.info('Central server: %s'%central_server)
    source_pub_key = os.path.join(base_ssh_dir_abs, 'id_rsa.pub')
    dest_pub_key = "%s:%s"%(central_server,os.path.join(base_ssh_dir, 'id_rsa.pub.%s'%name))
    print ('scp %s %s'%(source_pub_key, dest_pub_key))
    ret = subprocess.call(["scp", source_pub_key, dest_pub_key])

if __name__ == "__main__":
    main(sys.argv[1:])
