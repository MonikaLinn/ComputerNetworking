# Lab3 Skeleton

from pox.core import core
from netaddr import *
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Routing (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_routing (self, packet, packet_in, port_on_switch, switch_id):
    # port_on_swtich - the port on which this packet was received
    # switch_id - the switch which received this packet

    def accept(packet, packet_in, end_port):
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.actions.append(of.ofp_action_output(port = end_port))
      msg.data = packet_in
      self.connection.send(msg)

    def drop():
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 30
      msg.hard_timeout = 30
      msg.buffer_id = packet_in.buffer_id
      self.connection.send(msg)


    icmp = packet.find("icmp")
    tcp = packet.find("tcp")
    udp = packet.find("udp")
    ipv4 = packet.find("ipv4")

    Serv2 = IPAddress("200.20.1.1")
    ServWeb = IPAddress("200.20.1.2")
    ServDNS = IPAddress("200.20.1.3")
    ws1 = IPAddress("200.20.3.4")
    ws2 = IPAddress("200.20.3.5")
    ws3 = IPAddress("200.20.4.7")
    ws4 = IPAddress("200.20.4.6")
    Laptop1 = IPAddress("200.20.2.8")
    Laptop2 = IPAddress("200.20.2.9")
    Printer = IPAddress("200.20.2.10")
     
    subnets = {
      "ot_dep": IPNetwork('200.20.3.0/24'),
      "it_dep": IPNetwork('200.20.4.0/24'),
      "data_cen": IPNetwork('200.20.1.0/24'),
      "sales_dep": IPNetwork('200.20.2.0/24')
    }

    src_ip = IPAddress(str(ipv4.srcip))
    dst_ip = IPAddress(str(ipv4.dstip))

    if switch_id == 5: #CoreSwitch 
      print("In Switch 5")
      if dst_ip in subnets["ot_dep"]:
        port = 5
        accept(packet, packet_in, port)
      elif dst_ip in subnets["it_dep"]:
        port = 2
        accept(packet, packet_in, port)
      elif dst_ip in subnets["data_cen"]:
        port = 3
        accept(packet, packet_in, port)
      elif dst_ip in subnets["sales_dep"]:
        port = 4
        accept(packet, packet_in, port)
      else: 
        drop()    

    #OT Department
    elif switch_id == 1:
      print("In Switch 1")
      if tcp:
        if dst_ip in subnets["ot_dep"]:
          print("We are in the OT Department")  
          if dst_ip == ws1:
            port = 8
            print("Going to Workstation1")
            accept(packet, packet_in, port)
          elif dst_ip == ws2:
            print("Going to Workstation2")
            port = 9
            accept(packet, packet_in, port)
        if dst_ip in subnets["data_cen"] or dst_ip in subnets["it_dep"]: #go to core
          port = 5
          print("Going to core!")
          accept(packet, packet_in, port)

      if udp:
        if dst_ip in subnets["ot_dep"]:  
          print("UDP + OT")
          if dst_ip == ws1:
            port = 8
            print("Going to Workstation1")
            accept(packet, packet_in, port)
          elif dst_ip == ws2:
            port = 9
            print("Going to Workstation2")
            accept(packet, packet_in, port)
        if dst_ip in subnets["data_cen"]: #go to core
          port = 5
          print("Going to core!")
          accept(packet, packet_in, port)
      
      if icmp:
        if dst_ip in subnets["ot_dep"]:
          if dst_ip == ws1:
              port = 8
              print("Going to Workstation1")
              accept(packet, packet_in, port)
          if dst_ip == ws2:
              port = 9
              print("Going to Workstation1")
              accept(packet, packet_in, port)

    #IT Department        
    elif switch_id == 2:  
      print("In Switch 2")
      if tcp:
        if dst_ip in subnets["it_dep"]:
          print("TCP + IT")
          if dst_ip == ws3:
            port = 10
            print("Going to Workstation3")
            accept(packet, packet_in, port)
          if dst_ip == ws4:
            port = 11
            print("Going to Workstation4")
            accept(packet, packet_in, port)
        if dst_ip in subnets["ot_dep"] or dst_ip in subnets["data_cen"]:
          port = 2
          print("Going to core!")
          accept(packet, packet_in, port)

      if icmp:
        if dst_ip in subnets["it_dep"]:
          print("ICMP + IT")
          if dst_ip == ws3:
            port = 10
            print("Going to Workstation3")
            accept(packet, packet_in, port)
          if dst_ip == ws4:
            port = 11
            print("Going to Workstation4")
            accept(packet, packet_in, port)
        if dst_ip in subnets["sales_dep"]:
          port = 2
          print("Going to core!")
          accept(packet, packet_in, port)

      if udp:
        if dst_ip in subnets["it_dep"]:  
          print("UDP + IT")
          if dst_ip == ws3:
            port = 10
            print("Going to Workstation3")
            accept(packet, packet_in, port)
          elif dst_ip == ws4:
            port = 11
            print("Going to Workstation4")
            accept(packet, packet_in, port)
        if dst_ip in subnets["data_cen"]: #go to core
          port = 2
          print("Going to core!")
          accept(packet, packet_in, port)

    #Data Center
    elif switch_id == 3:  
      print("In Switch 3")
      if tcp:
        if dst_ip in subnets["data_cen"]:
          print("TCP + Data")
          if dst_ip == IPAddress(Serv2):
            port = 13
            print("Going to Serv2")
            accept(packet, packet_in, port)
          if dst_ip == ServDNS:
            port = 14
            print("Going to ServDNS")
            accept(packet, packet_in, port)
          if dst_ip == ServWeb:
            port = 15
            print("Going to ServWeb")
            accept(packet, packet_in, port)
        if dst_ip in subnets["it_dep"] or dst_ip in subnets["ot_dep"]:
          port = 3
          print("Going to Core!")
          accept(packet, packet_in, port)

      if udp:
        if dst_ip in subnets["data_cen"]:
          print("UDP + Data")
          if dst_ip == Serv2:
            port = 13
            accept(packet, packet_in, port) 
          if dst_ip == ServDNS:
            port = 14
            accept(packet, packet_in, port)
          if dst_ip == ServWeb:
            port = 15
            accept(packet, packet_in, port)
        if dst_ip in subnets["it_dep"] or dst_ip in subnets["ot_dep"]:
          port = 3
          print("Going to Core!")
          accept(packet, packet_in, port)

      if icmp:
        if dst_ip in subnets["data_cen"]:
          print("ICMP + IT")
          if dst_ip == Serv2:
            port = 13
            print("Going to Server2")
            accept(packet, packet_in, port)
          if dst_ip == ServDNS:
            port = 14
            print("Going to DNSserver")
            accept(packet, packet_in, port)
          if dst_ip == ServWeb:
            port = 15
            print("Going to WebServer")
            accept(packet, packet_in, port)
        
    #Sales Department    
    elif switch_id == 4:  
      print("In Switch 4")
      if icmp:
        if dst_ip in subnets["sales_dep"]:
          print("ICMP + Sales!")
          if dst_ip == Laptop1:
            print("We are going to Laptop1!")
            port = 6
            accept(packet, packet_in, port)
          elif dst_ip == Laptop2:
            print("We are going to Laptop2!")
            port = 7
            accept(packet, packet_in, port)
          elif dst_ip == Printer:
            port = 12
            accept(packet, packet_in, port)
        if dst_ip in subnets["it_dep"]:
          port = 4
          print("Going to Core!")
          accept(packet, packet_in, port)

      if tcp:
        if dst_ip in subnets["sales_dep"]:
          print("TCP + Sales!")
          if dst_ip == Laptop1:
            port = 6
            accept(packet, packet_in, port)
          if dst_ip == Laptop2:
            port = 7
            accept(packet, packet_in, port)
          if dst_ip == Printer:
            port = 12
            accept(packet, packet_in, port)

      if udp:
        if dst_ip in subnets["sales_dep"]:
          print("UDP + Sales!")
          if dst_ip == Laptop1:
            port = 6
            accept(packet, packet_in, port)
          if dst_ip == Laptop2:
            port = 7
            accept(packet, packet_in, port)
          if dst_ip == Printer:
            port = 12
            accept(packet, packet_in, port)
    pass

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_routing(packet, packet_in, event.port, event.dpid)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Routing(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
