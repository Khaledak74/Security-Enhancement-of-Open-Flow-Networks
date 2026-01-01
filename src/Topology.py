from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI

def myNetwork():
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)

    # Add controllers
    c0 = net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6102)
    c1 = net.addController(name='c1', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6103)

    # Add core switches
    core1 = net.addSwitch('core1')
    core2 = net.addSwitch('core2')

    # Add access switches
    access1 = net.addSwitch('access1')
    access2 = net.addSwitch('access2')
    access3 = net.addSwitch('access3')
    access4 = net.addSwitch('access4')

    # Connect core switches to access switches
    net.addLink(core1, access1)
    net.addLink(core1, access2)
    net.addLink(core2, access3)
    net.addLink(core2, access4)

    # Add link between core switches
    net.addLink(core1, core2)

    # Add hosts
    hosts = []
    for i in range(1, 17):
        host = net.addHost('h{}'.format(i), defaultRoute='via eth0')
        hosts.append(host)
        if i <= 4:
            net.addLink(host, access1)
        elif i <= 8:
            net.addLink(host, access2)
        elif i <= 12:
            net.addLink(host, access3)
        else:
            net.addLink(host, access4)

    # Enable NAT
    nat = net.addNAT('nat')
    net.addLink(nat, core1)
    net.addLink(nat, core2)

    # Build and start the network
    net.build()

    core1.start([c0])
    core2.start([c1])

    net.start()
    nat.cmd('sysctl net.ipv4.ip_forward=1')  # Enable IP forwarding on NAT
    nat.cmd('iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')  # Enable NAT on NAT interface

    # Set default gateway on each host
    for i in range(1, 17):
        host = net.get('h{}'.format(i))
        host.setDefaultRoute('via {}'.format(host.defaultIntf().IP()))

    CLI(net)
    net.stop()

if __name__ == '__main__':
    myNetwork()