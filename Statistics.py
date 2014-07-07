def _timer_func ():
  for connection in core.openflow._connections.values():
    #print connection.dpid
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
  #ppp=event.parsed
  print event.dpid
  #print ppp.payload.srcip
  #print ppp.src
  #print event.ofp.in_port
  log.debug("FlowStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)

  # Get number of bytes/packets in flows for web traffic only
  web_bytes = 0
  web_flows = 0
  web_packet = 0
  for f in event.stats:
    if f.match.tp_dst or f.match.tp_src:
      web_bytes += f.byte_count
      web_packet += f.packet_count
      web_flows += 1
      #print f.match.nw_src, f.match.nw_dst,f.match.tp_src,f.match.tp_dst

      #######################################
      try:
        snum=event.connection.dpid
        self.link_cost[snum][self.port_switch[snum][in_port]]= byte_count/5
      except Exception:
          pass
      ##############################################

  log.info("Web traffic from %s: %s bytes (%s packets) over %s flows", 
    dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)
      
# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("PortStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)
######################################################
