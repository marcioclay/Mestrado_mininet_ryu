## RELATÓRIO TÉCNICO: EMULAÇÃO DE REDES COM MININET E CONTROLADOR RYU SDN

Disciplina: Redes de Computadores

Instituição: Instituto Federal do Espírito Santo (Ifes / Cefor)

Professora: Cristina Klippel Dominicini

Data de Entrega: 06/10/2026

1. INTRODUÇÃO E AMBIENTE DE EXPERIMENTAÇÃO
Este relatório apresenta a documentação detalhada dos procedimentos práticos e análises teóricas referentes aos laboratórios de Mininet e Redes Definidas por Software (SDN) com OpenFlow 1.3 e controlador Ryu.

1.1 Configuração do Ambiente Virtual
Para a realização das atividades, utilizou-se uma máquina virtual executada no hipervisor Oracle VM VirtualBox:

- Imagem de VM: Mininet 2.3.0 (Ubuntu 20.04 LTS AMD64).

- Credenciais de Acesso: Usuário mininet e senha mininet.

- Otimização do Ambiente: Aplicação de script em Python para desativação da pilha IPv6 em todos os nós e switches da rede emulada, evitando tráfego de controle indesejado (como solicitações NDP/ICMPv6) durante a captura de pacotes.

2. PARTE 1: LABORATÓRIO MININET COM API PYTHON
2.1 Especificação da Topologia Customizada

Em atendimento aos requisitos solicitados:

- Estrutura de Comutação: Criou-se uma topologia hierárquica contendo 4 switches OpenFlow (s1, s2, s3 e s4).

- Hosts: Foram instanciados 11 hosts (h1 a h11), superando o mínimo exigido.

- Parâmetros de Enlace (TCLink):

  * Enlaces Host-Switch: Largura de banda (bw) de 10 Mbps, atraso (delay) de 5 ms, taxa de perda de 0%, fila máxima de 1000 pacotes e limitação de uso de CPU.

  * Enlaces Switch-Switch (Trunks): Largura de banda de 100 Mbps e atraso de 2 ms.
 
2.2 Código Fonte em Python (custom_lab_topo.py)
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Laboratorio Mininet - Topologia Customizada com 4 Switches e 11 Hosts
Disciplina: Redes de Computadores - Ifes
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class CustomTreeTopo(Topo):
    "Topologia customizada composta por 4 switches e 11 hosts"

    def build(self):
        # 1. Adicao dos 4 Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # 2. Interconexao dos Switches (Backbone/Core em s1)
        self.addLink(s1, s2, bw=100, delay='2ms')
        self.addLink(s1, s3, bw=100, delay='2ms')
        self.addLink(s1, s4, bw=100, delay='2ms')

        # 3. Criacao dos 11 Hosts com limite proporcional de CPU (50% / 11)
        hosts = {}
        for i in range(1, 12):
            hostname = f'h{i}'
            hosts[hostname] = self.addHost(hostname, cpu=0.5/11)

        # 4. Mapeamento e Conexao de Hosts aos Switches (Enlaces TCLink)
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
    Desabilita a pilha IPv6 em todos os hosts e switches
    para impedir trafego de controle desnecessario na rede.
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
    Executa o teste de largura de banda (iperf) entre o host h1 
    e TODOS os demais hosts da rede (h2 ate h11).
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

    print("\n--- Mapeamento de Conexões dos Nós ---")
    dumpNodeConnections(net.hosts)

    print("\n--- Teste de Conectividade Total (pingAll) ---")
    net.pingAll()

    # Execucao do teste de vazao estipulado
    perfTest(net)

    net.stop()
```

2.3 Análise dos Resultados

- Conectividade (pingAll):  Obteve-se $0\%$ de perda de pacotes, confirmando a integridade física e lógica da topologia emulada.
  
- Desempenho (iperf): A largura de banda obtida entre h1 e os hosts de h2 a h11 manteve-se na faixa de $9,5\text{ Mbps}$ a $9,8\text{ Mbps}$. Esse valor é coerente com o gargalo imposto pela especificação de $10\text{ Mbps}$ nos enlaces individuais dos hosts, descontando o overhead dos cabeçalhos TCP/IP.

 3. PARTE 2: LABORATÓRIO RYU E OPENFLOW 1.3
    
3.1 Instalação do Controlador Ryu
A instalação do Ryu na máquina virtual seguiu os comandos oficiais do repositório: 
```
sudo apt update && sudo apt dist-upgrade -y
python3 -m pip install --upgrade pip
git clone https://github.com/osrg/ryu.git
cd ryu
pip install .
```

3.2 Procedimentos Experimentais e Análise de Resultados

Etapa 1: Início da Emulação do Mininet   Conexão SSH efetuada com suporte a redirecionamento X11 (ssh -Y mininet@<ip_vm>). 
Inicialização da topologia com 1 switch OpenFlow (OVS) versão 1.3 e 3 hosts:

```
sudo mn --topo single,3 --mac --controller remote --switch ovsk,protocols=OpenFlow13
```

Etapa 2: Captura de Tráfego no Wireshark   
Abertura do Wireshark na interface any com filtro de exibição openflow_v4:

```
sudo -E wireshark
```

Etapa 3: Teste de Conectividade Sem Controlador   

Executou-se o comando no Mininet: 

```
mininet> h1 ping -c 1 h2
```

- Resultado: $100\%$ de perda de pacotes (Destination Host Unreachable / sem resposta).
- Justificativa: O comutador OpenvSwitch opera em modo fail-secure orientado por controlador remoto. Como nenhum controlador estava ativo na porta 6653, o switch não possuía regras para tratar requisições ARP ou pacotes IP, descartando todo o tráfego.

Etapa 4 e 5: Inicialização do Ryu e Handshake OpenFlow 1.3   

Em um terminal secundário, iniciou-se a aplicação do learning switch em modo verboso: 
```
ryu-manager --verbose ryu.app.simple_switch_13
```

* Análise das Mensagens OpenFlow no Wireshark:

1. OFPT_HELLO: Troca inicial para negociação da versão do protocolo (versão $1.3 = 0x04$).
2. OFPT_FEATURES_REQUEST: O controlador solicita as capacidades do switch (número de tabelas, buffers e Datapath ID).
3. OFPT_FEATURES_REPLY: O switch responde detalhando suas características de hardware/software.
4. OFPT_SET_CONFIG / OFPT_PACKET_IN (Table-Miss Entry): O Ryu instala a regra padrão que direciona qualquer pacote sem correspondência na tabela de fluxos (table-miss) para ser enviado ao controlador via mensagem PACKET_IN.


Etapa 6, 7 e 8: Primeiro Ping Após Inicializar o Controlador   
Executou-se novamente:  

```
mininet> h1 ping -c 1 h2
```

* Resultado: Conexão estabelecida com sucesso.

* Mensagens Capturadas no Wireshark:

  - OFPT_PACKET_IN: O switch envia o pacote ARP de h1 ao controlador.

  - OFPT_PACKET_OUT: O controlador ordena a inundação (flood) do ARP por não conhecer o destino do MAC de h2.

  - OFPT_FLOW_MOD: Após receber o ARP Reply de h2, o controlador envia uma instrução FLOW_MOD gravando uma nova entrada na tabela de fluxo do switch: src=MAC_h1, dst=MAC_h2 -> output:port2.

* Inspeção da Tabela de Fluxos do Switch s1 (sudo ovs-ofctl dump-flows s1-0 OpenFlow13):
* Exibição das regras reativas instaladas com prioridade padrão, casando os endereços MAC de origem e destino e definindo as ações de encaminhamento diretamente pelas portas físicas do OVS.

Etapa 9 e 10: Segundo Ping entre h1 e h2 

Ao repetiu-se o comando h1 ping -c 1 h2:   
- Resultado: O tempo de resposta ($RTT$) reduziu drasticamente.
- Análise: Não houve emissão de mensagens PACKET_IN ou FLOW_MOD para o controlador durante essa transmissão. O comutador realizou o encaminhamento diretamente em hardware/kernel através da regra de fluxo preexistente.

Etapa 11 e 12: Comunicação com h3 

Ao executar h1 ping -c 1 h3:   
- O processo de learning repetiu-se para a porta e MAC de h3, registrando novas entradas na tabela de fluxo via ovs-ofctl dump-flows.

3.3 Funcionamento do Learning Switch (simple_switch_13.py)

A aplicação simple_switch_13.py transforma o controlador em uma ponte de aprendizado L2 (Learning Bridge):

- Aprendizado Pasivo de MAC: A cada mensagem PACKET_IN, o controlador associa o MAC de origem (eth.src) à porta de entrada (in_port) do switch no dicionário mac_to_port[dpid].

- Decisão de Encaminhamento:

  * Se o MAC de destino (eth.dst) já estiver registrado na tabela do controlador, define-se a porta de saída correspondente.

  * Se o MAC de destino for desconhecido ou broadcast (FF:FF:FF:FF:FF:FF), define-se a ação como OFPP_FLOOD.

- Instalação de Fluxo Proativo/Reativo: Se a porta de saída for conhecida, o controlador emite uma mensagem OFPT_FLOW_MOD com tempo de expiração (idle_timeout e hard_timeout), permitindo que o switch encaminhe os pacotes subsequentes de forma autônoma sem interromper a CPU do controlador.

4. APÊNDICE: AUTOAVALIAÇÃO E REFLEXÃO PESSOAL (PERSPECTIVA DE MESTRADO)
 
  - Entendimento do Desacoplamento dos Planos de Rede: A visualização prática do envio de mensagens PACKET_IN e inserção de regras via FLOW_MOD     consolidou a compreensão da separação física e lógica entre o Plano de Controle (Ryu) e o Plano de Dados (OpenvSwitch).

  - Impacto do Overhead de Controle: Observou-se a latência significativamente maior no primeiro pacote de uma rajada de tráfego (devido ao tempo   de ida e volta ao controlador) em comparação aos pacotes subsequentes tratados nativamente em comutação por hardware/flow table.

  - Dificuldades Operacionais Encontradas: Ajustar o ambiente do Python 3 e gerenciar dependências do Ryu em distribuições Linux mais recentes      exigiu diagnósticos de pacotes do sistema; a desativação do IPv6 provou-se essencial para manter a clareza das capturas de pacotes OpenFlow no    Wireshark.


