#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Laboratorio Mininet - Topologia Customizada (4 Switches e 11 Hosts)
Disciplina: Redes de Computadores - Ifes
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class CustomTreeTopo(Topo):
    "Topologia composta por 4 switches e 11 hosts"

    def build(self):
        # 1. Adicao dos 4 Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # 2. Interconexao dos Switches (Backbone/Trunks a 100 Mbps)
        self.addLink(s1, s2, bw=100, delay='2ms')
        self.addLink(s1, s3, bw=100, delay='2ms')
        self.addLink(s1, s4, bw=100, delay='2ms')

        # 3. Criacao dos 11 Hosts com limite proporcional de CPU
        hosts = {}
        for i in range(1, 12):
            hostname = f'h{i}'
            hosts[hostname] = self.addHost(hostname, cpu=0.5/11)

        # 4. Parametros dos Enlaces dos Hosts (10 Mbps, 5ms delay, 1000 queue)
        link_opts = dict(bw=10, delay='5ms', loss=0, max_queue_size=1000, use_htb=True)

        # Distribuicao dos Hosts nos Switches:
        # s1 -> h1, h2
        self.addLink(hosts['h1'], s1, **link_opts)
        self.addLink(hosts['h2'], s1, **link_opts)

        # s2 -> h3, h4, h5
        self.addLink(hosts['h3'], s2, **link_opts)
        self.addLink(hosts['h4'], s2, **link_opts)
        self.addLink(hosts['h5'], s2, **link_opts)

        # s3 -> h6, h7, h8
        self.addLink(hosts['h6'], s3, **link_opts)
        self.addLink(hosts['h7'], s3, **link_opts)
        self.addLink(hosts['h8'], s3, **link_opts)

        # s4 -> h9, h10, h11
        self.addLink(hosts['h9'], s4, **link_opts)
        self.addLink(hosts['h10'], s4, **link_opts)
        self.addLink(hosts['h11'], s4, **link_opts)


def disable_ipv6(net):
    """
    Desabilita a pilha IPv6 nos hosts e switches para evitar sobrecarga.
    """
    for h in net.hosts:
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")


def perfTest(net):
    """
    Testa a largura de banda (iperf) entre h1 e TODOS os demais hosts (h2 a h11).
    """
    print("\n=======================================================")
    print(" INICIANDO AVALIACAO DE LARGURA DE BANDA (iperf)")
    print("=======================================================")
    
    h1 = net.get('h1')
    for i in range(2, 12):
        target_name = f'h{i}'
        target_host = net.get(target_name)
        print(f"\n[TESTE IPERF] Medindo banda entre h1 e {target_name}:")
        net.iperf((h1, target_host))


if __name__ == '__main__':
    setLogLevel('info')
    
    topo = CustomTreeTopo()
    net = Mininet(
        topo=topo,
        host=CPULimitedHost,
        link=TCLink
    )
    
    net.start()
    disable_ipv6(net)

    print("\n--- Mapeamento de Conexoes dos Nos ---")
    dumpNodeConnections(net.hosts)

    print("\n--- Teste de Conectividade Total (pingAll) ---")
    net.pingAll()

    # Execucao dos testes do iperf
    perfTest(net)

    net.stop()
