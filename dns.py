import glob
import json
import socket
from dnstypes import DNSPacket

def main():
    PORT = 53
    IP = '127.0.0.1'
    ZONES = load_zonefiles()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    print('listening on', IP, PORT)
    while True:
        try:
            data, addr = sock.recvfrom(512)
            print('\n[+] new connection received from', addr)

            packet = DNSPacket(data)
            packet.compute_responses(ZONES)
            out = packet.serialize()
            
            sock.sendto(out, addr)

        except Exception as err:
            raise err

def load_zonefiles():
    jsonzone = {}
    for zone in glob.glob('zones/*.zone'):
        with open(zone) as fp:
            obj = json.load(fp)
            name = obj.get('$origin')

            if not name:
                print('ERROR loading', zone)
                continue

            jsonzone[name] = obj
    return jsonzone

if __name__ == '__main__':
    main()
