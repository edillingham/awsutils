import functions

def get_php_configs(ssh_path, user, host, debug=False):
    cmd = '"{0}" -ssh {1}@{2} "/usr/bin/php -i | grep \'upload_max_filesize\|post_max_size\'"'.format(ssh_path, user, host)
    if debug:
        print(cmd)
        
    output, error = functions.run_command(cmd, printError=debug)

    if error:
        return {'error': error}

    d = {}
    for var in output.strip().split('\n'):
        vals = var.split(' => ')
        d[vals[0]] = vals[1]

    return d
