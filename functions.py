import subprocess

# run a shell command and return its entire output
def run_command(cmds, printError=False, returnError=False):
    sp = subprocess.Popen(cmds, \
                          stdout=subprocess.PIPE, \
                          stderr=subprocess.PIPE, \
                          shell=True)
    out, err = sp.communicate()

    if err and printError:
        print(err.decode('ascii'))

    return out.decode('ascii').strip(), \
           err.decode('ascii').strip()
