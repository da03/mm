import sys, argparse, logging, subprocess

from utils import parse_params

def process_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--name', dest="name",
                        type=str,
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

    # read config file
    params = parse_params(parameters.config_path)
    # add public key file to central server public key file
    assert 'central' in params, 'central server must be set in config file %s. The required format is \'central: username@machine-ip\''%parameters.config_path
    logging.info('Central server: %s'%params['central'])
    subprocess.call("exit 1", shell=True)

if __name__ == "__main__":
    main(sys.argv[1:])
