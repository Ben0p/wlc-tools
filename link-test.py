import paramiko
import time
from datetime import datetime
import getpass


def login(ip, un, pw):
    print('Logging in to WLC...')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip, port=22, username=un, password=pw)
    connection = client.invoke_shell()
    connection.settimeout(1)
    time.sleep(1)
    connection.send(un+'\r')
    time.sleep(1)
    connection.send(pw+'\r')
    time.sleep(1)
    output = connection.recv(9999).decode(encoding='utf-8')

    lastline = output.splitlines()[-1]
    if lastline == "User:":
        print("Login failed, try again...")
        return(False)

    else:
        print('Logged in!')
        return(connection)


def showMeshPath(ap):

    print(f"Checking mesh path for {ap}...")

    meshPath = {}
    hops = []

    try:
        output = connection.recv(9999).decode(encoding='utf-8')
    except:
        pass


    connection.send(f'show mesh path {ap}\r')
    time.sleep(0.5)
    output = connection.recv(9999).decode(encoding='utf-8')
    lines = output.splitlines()

    meshPath['ap'] = ap
    if lines[2] == 'Cisco AP name is invalid.':
        meshPath['online'] = False
        return(meshPath)

    else:
        meshPath['online'] = True
        meshPath['root'] = root_ap = lines[-2].split()[0]
        del lines[0:5]
        del lines[-2:]
        for idx, ap in enumerate(lines):
            
            ap = ap.split()
            stats = {

                'ap' : ap[0],
                'channel' : ap[1],
                'rate' : ap[2],
                'snr' : ap[3],
                'hop' : idx+1
            }
            hops.append(stats)
        
        meshPath['hops'] = hops

        return(meshPath)

def linkTest(child, parent, settings):

    print(f'Link test {child} -> {parent}')

    link = {}
    try:
        output = connection.recv(9999).decode(encoding='utf-8')
    except:
        pass

    command = (f"config mesh linktest "
    f"{child} "
    f"{parent} "
    f"{settings['data_rate']} "
    f"{settings['packets_per_second']} "
    f"{settings['packet_size']} "
    f"{settings['duration']}\r")

    connection.send(command)

    counter(int(settings['duration'])+3)

    output = connection.recv(9999).decode(encoding='utf-8')
    lines = output.splitlines()

    link['source'] = child
    link['destination'] = parent

    try:
        snr = lines[21].split()[1][:-1]
        rssi = lines[37].split()[1][:-1]
        error = lines[45].split()[-1][:-1]

        link['snr'] = snr
        link['rssi'] = rssi
        link['error'] = error
        link['status'] = True

    except:
        link['status'] = False
    
    return(link)

def getSettings():
    settings ={}

    print("Retrieving settings...")
    try:
        with open('settings.txt', 'r') as f:
            for line in f:
                line = line.strip()
                setting, parameter = line.split('=')
                settings[setting] = parameter
    except:
        input("Failed to open settings.txt")

    settings['password'] = getpass.getpass()
    

    return(settings)

def counter(sec):
    interval = sec/100
    
    for i in range(101):       # for 0 to 100
        s = str(i) + '%'       # string for output
        print(s, end='')       # just print and flush
        print('\r', end='')    # back to the beginning of line    
        time.sleep(interval)   # sleep for 200ms


if __name__ == '__main__':

    while True:
        settings = getSettings()
        connection = login(settings['wlc_ip'], settings['wlc_username'], settings['password'])
        if connection:
            break


    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    out_file_name = f'{timestamp} - Link Tests.csv'

    with open(settings['maps_file'], 'r') as maps:
        with open(out_file_name, 'w', 5) as tests:
            tests.write('time,source,destination,snr,rssi,error,result\n')
            for line in maps:
                if line[0] == '#':
                    continue
                _map = line.strip()
                testtime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                mesh_path = showMeshPath(_map)
                time.sleep(0.5)
                if mesh_path['online']:
                    source = mesh_path['ap']
                    dest = mesh_path['hops'][0]['ap']
                    testtime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    res = linkTest(source, dest, settings)
                    if res['status']:
                        tests.write(f"{testtime},{res['source']}, {res['destination']}, {res['snr']}, {res['rssi']}, {res['error']}, success\n")
                    else:
                        tests.write(f"{testtime},{res['source']}, {res['destination']}, 0, 0, 0, offline\n")
                    
                    if settings['both_ways'] == 'true':
                        dest = mesh_path['ap']
                        source = mesh_path['hops'][0]['ap']
                        testtime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        res = linkTest(source, dest, settings)
                        if res['status']:
                            tests.write(f"{testtime},{res['source']}, {res['destination']}, {res['snr']}, {res['rssi']}, {res['error']}, success\n")
                        else:
                            tests.write(f"{testtime},{res['source']}, {res['destination']}, 0, 0, 0, offline\n")

                else:
                    tests.write(f"{testtime},{_map}, 0, 0, 0, 0, offline\n")
                tests.flush()

            tests.close()
        maps.close()
