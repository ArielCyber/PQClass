from nfstream import NFPlugin


class TDL(NFPlugin):
    """TDL(Time,packet-Direction,packet Length) |
    A 2D matrix of extract Time,packet-direction and
    packet length from each packet.

    Output Features:
        Select all packets from each flow and extract Time,
        packet-direction and packet length from each packet.
    """

    def on_init(self, packet, flow):
        """ """
        flow.udps.port_TDL = list()
        flow.udps.ip_TDL = list()
        src_port = packet.src_port <= 1024
        dst_port = packet.dst_port <= 1024
        # session direction by port
        if src_port and not dst_port:  # 1,0
            flow.udps.port_direction = 1
        elif not src_port and dst_port:  # 0,1
            flow.udps.port_direction = 0
        else:  # 0,0 and 1,1
            # check which port is smaller
            if packet.src_port < packet.dst_port:
                flow.udps.port_direction = 1
            else:
                flow.udps.port_direction = 0
        if flow.ip_version == 4:  # dst ip is ipv4
            # src_ip = packet.src_ip.split('.')
            dst_ip = packet.dst_ip.split(".")
            if (
                int(dst_ip[0]) == 10
                or (
                    int(dst_ip[0]) == 172
                    and 16 <= int(dst_ip[1])
                    and int(dst_ip[1]) <= 31
                )
                or (int(dst_ip[0]) == 192 and int(dst_ip[1]) == 168)
            ):
                flow.udps.ip_direction = 1
            else:
                flow.udps.ip_direction = 0
        if flow.ip_version == 6:  # dst ip is ipv6
            # src_ip = packet.src_ip[:packet.src_ip.find(':')]
            dst_ip = packet.dst_ip[: packet.dst_ip.find(":")]
            if dst_ip == "fe80" or dst_ip == "fc00" or dst_ip == "fec0":
                flow.udps.ip_direction = 1
            else:
                flow.udps.ip_direction = 0
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        """ """
        # s_packet = Ether()
        if packet.protocol in [6, 17]:  # TCP or UDP only.
            vf_port = list()
            vf_ip = list()
            # vf_port.append(packet.time/1000) # timestamp (seconds)
            # vf_ip.append(packet.time/1000) # timestamp (seconds)
            # vf.append(packet.delta_time) # inter arrival time
            # vf.append(packet.time - flow.bidirectional_first_seen_ms) # relative time

            if len(vf_port) < 30 and len(vf_ip) < 30:

                if flow.udps.port_direction == 0:
                    vf_port.append(abs(packet.direction - 1))  # packet direction
                else:
                    vf_port.append(packet.direction)

                if flow.udps.ip_direction == 0:
                    vf_ip.append(abs(packet.direction - 1))  # packet direction
                else:
                    vf_ip.append(packet.direction)

                vf_port.append(packet.ip_size)  # packet size
                vf_ip.append(packet.ip_size)  # packet size
                # relative time
                vf_port.append(packet.time - flow.bidirectional_first_seen_ms)
                # relative time
                vf_ip.append(packet.time - flow.bidirectional_first_seen_ms)
                # append packet feature vector to list
                flow.udps.port_TDL.append(vf_port)
                # append packet feature vector to list
                flow.udps.ip_TDL.append(vf_ip)

    def on_expire(self, flow):
        del flow.udps.port_direction
        del flow.udps.ip_direction
