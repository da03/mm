import sys, subprocess, shutil

if __name__ == '__main__':
    name = sys.argv[1]
    user_name = sys.argv[2]
    host_name = sys.argv[3]
    public_ip = sys.argv[4]

    ssh_relative_path = '~/.ssh'
    # figure out paths
    home_abs_path = os.path.expanduser('~')
    app_abs_path = os.path.dirname(os.path.realpath(__file__))
    app_relative_path = app_dir.replace(app_abs_path, '~')

    key_file_path  = os.path.join(app_relative_path, 'keys', 'id_rsa.pub.%s'%name)

    authorized_keys_path = os.path.join(ssh_relative_path, 'authorized_keys')
    tmp_authorized_keys_path = os.path.join(ssh_relative_path, 'authorized_keys.tmp')
    # create authorized_keys if not present
    if not os.path.isfile(authorized_keys_path):
        f = open(authorized_keys_path, 'w')
        f.close()

    # add to authorized_keys
    #shutil.copy(authorized_keys_path, tmp_authorized_keys_path)
    
    with open(authorized_keys_path) as fin:
        with open(tmp_authorized_keys_path, 'w') as fout:
            for line in fin:
                if '%s@%s'%(user_name, host_name) in line:
                    continue
                fout.write(line)
            fout.write(open(key_file_path).readline())
    shutil.move(tmp_authorized_keys_path, authorized_keys_path)

    machine_path = os.path.join(app_relative_path, 'config.txt')
    tmp_machine_path = os.path.join(app_relative_path, 'config.txt.tmp')
    with open(machine_path, 'r') as fin:
        with open(tmp_machine_path, 'w') as fout:
            for line in fin:
                m = re.match('%s[: =].*'%name, line.strip())
                if m:
                    continue
                fout.write(line)
            m = re.match(r'.*\.[a-zA-Z]+', host_name)
            if m:
                fout.write('%s: %s@%s\n'%(name, user_name, host_name))
            else:
                fout.write('%s: %s@%s\n'%(name, user_name, public_ip))
    shutil.move(tmp_machine_path, machine_path)
