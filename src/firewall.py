from pox.core import core
import pox.openflow.libopenflow_01 as of
import time

log = core.getLogger()

Threshold for rate limiting (total SYN packets per second)
THRESHOLD = 100

Tracking total SYN packets
total_syn_packets = 0
last_cleared = 0

Function to check if IP is within the subnet
def is_in_subnet(ip_addr):
parts = ip_addr.split('.')
if len(parts) < 1:
return False
first_octet = int(parts[0])
return first_octet == 10

def drop_packet(event, reason):
         packet = event.parsed
         msg = of.ofp_flow_mod()
         msg.match = of.ofp_match.from_packet(packet, event.port)
         msg.idle_timeout = 10
         msg.hard_timeout = 30
         msg.priority = 65535
         msg.actions = []  # Empty actions list means drop
         event.connection.send(msg)
         log.warning("Dropping packet: {}".format(reason))

def _handle_PacketIn(event):
         global total_syn_packets, last_cleared
         packet = event.parsed
         ip_packet = packet.find('ipv4')
         tcp_packet = packet.find('tcp')
       
current_time = time.time()
#Clear old entries every second
         if current_time - last_cleared > 1:
         total_syn_packets = 0
         last_cleared = current_time

#Check if it's a TCP packet with the SYN flag set
         if tcp_packet and tcp_packet.SYN:
         total_syn_packets += 1

#If the total SYN packet rate exceeds the threshold, drop the packet 
        if total_syn_packets > THRESHOLD:
        drop_packet(event, "SYN flood detection")
return

#Check if the source IP is within the subnet 10.0.0.0/8
if ip_packet and not is_in_subnet(ip_packet.srcip.toStr()):
         drop_packet(event, "from {} as it is outside the allowed             subnet".format(ip_packet.srcip))
return

#Normal packet handling
       msg = of.ofp_packet_out()
       msg.data = event.ofp
       msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
       msg.in_port = event.port
event.connection.send(msg)

def launch():
         core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
         log.info("Firewall module loaded.")