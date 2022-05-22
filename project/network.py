from threading import Thread
from requests import post
from netifaces import interfaces, ifaddresses, AF_INET, AF_INET6


def all_network_interfaces():
    intfs = set()
    
    for intf_name in interfaces():
        intf = ifaddresses(intf_name)
        intf_entry = [intf_name]
        
        try:
            ipv4 = intf[AF_INET][0]['addr']
            if ipv4 == '127.0.0.1':
                continue
            intf_entry.append(ipv4)
        except (KeyError, IndexError):
            pass

        try:
            ipv6 = intf[AF_INET6][0]['addr']
            if ipv6.lower().startswith('fe80:'):
                continue
            if '%' in ipv6:
                ipv6 = ipv6[:ipv6.index('%')]
            intf_entry.append(ipv6)
        except (KeyError, IndexError):
            pass
        
        if len(intf_entry) > 1:
            intfs.add(tuple(intf_entry))
        
    return intfs


def user_selection():
    all_intfs = all_network_interfaces()

    if not all_intfs:
        print('\nNo network interface available!')
        if input('Run server on localhost?  Yes/No: ').strip().lower().startswith('y'):
            return '127.0.0.1'
        exit()
    
    wlan = list(filter(lambda x: x[0].startswith('wlan'), all_intfs))
    wlan.sort(key=lambda x: x[0])
    
    rmnet_data = list(filter(lambda x: x[0].startswith('rmnet_data'), all_intfs))
    rmnet_data.sort(key=lambda x: x[0])
    
    intfs = wlan + rmnet_data + list(all_intfs - set(wlan) - set(rmnet_data))

    print('Select network interface to host the server:')
    for i, intf in enumerate(intfs):
        print(f'\n{[i]} {intf[0]}')
        for j, addr in enumerate(intf[1:]):
            print(f'    {[j]} {addr}')
        
    response = input('\nEnter the index of your selection: ').strip()

    if response == '-1':
        return '127.0.0.1'

    if response == '':
        return intfs[0][1]

    if len(response) == 1:
        response += '0'

    if len(response) == 2:
        try:
            return intfs[int(response[0])][int(response[1]) + 1]
        except (IndexError, ValueError):
            pass
        
    print('\nInvalid input !')
    exit()


def publish_socket(sock):
    def mysocket():
        try:
            res = post(f'https://akshaynile.pythonanywhere.com/mysocket?socket={sock}')
            if res.text == 'success':
                print(' * Socket publication was successful ✔️\n')
        except Exception:
            print(' * Socket publication attempt failed ❌\n')

    Thread(target=mysocket).start()
