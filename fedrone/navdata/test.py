from fedrone.navdata.networking import NavDataSocket
import select
import pprint

a = NavDataSocket()
while True:
    b, c, d = select.select([a.socket], [], [])

    if a.socket in b:
        a.handle_socket_data()

        while a.has_more_nav_data():
            f = a.next_nav_data()
            print f.header
            pprint.pprint(dict(f.options))
