import socket


def get_host_and_ipv4():
    addr = []

    host_name = socket.gethostname()
    addr.append(host_name)
    ip_list = socket.getaddrinfo(host_name, None)
    for item in ip_list:
        ip = item[4][0]
        if '.' in ip:
            addr.append(ip)
    return addr


if __name__ == "__main__":
    ipv4_addresses = get_host_and_ipv4()
    for ip in ipv4_addresses:
        print(ip)
