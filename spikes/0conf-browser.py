import socket

from zeroconf import ServiceBrowser, Zeroconf

class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))
        info = zeroconf.get_service_info(type, name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

        if name.startswith('FGO Agent'):
            print("It is an FGO Agent")
            print(f"UUID:{info.properties[b'uuid']}")
            print(f"IP Address: {socket.gethostbyname(info.server)}")


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()
