## 🛠️ Etapa 3: Instalação do Ryu e Teste do OpenFlow 1.3 sem Controlador

### 1. Instalação do Controlador Ryu

Atualização do ambiente e instalação do controlador SDN Ryu a partir do repositório oficial[cite: 5, 13]:

```bash
sudo apt update
python3 -m pip install --upgrade pip
git clone [https://github.com/osrg/ryu.git](https://github.com/osrg/ryu.git)
cd ryu
pip install .

```

### 2. Inicialização da Topologia com OpenFlow 1.3

Inicialização do ambiente de emulação no Mininet com 1 switch e 3 hosts, configurado para utilizar a versão OpenFlow 1.3 e comunicar com um controlador remoto:

```
sudo mn --topo single,3 --mac --controller remote --switch ovsk,protocols=OpenFlow13
```
![Topo com Openflow](./imagens/4_mininet_ryu.png)

### 3. Teste de Comunicação sem Controlador Ativo

Verificação da conectividade entre os hosts h1 e h2 através do comando ping no terminal do Mininet:
```
mininet> h1 ping -c 1 h2
```
Perda 100%, pois o controlador não foi iniciado e não preencheu a tabela de fluxos.

![Falha de comunicação](./imagens/5_falha_ryu.png) 


### 4. Ativar controlador ryu

```
ryu-manager --verbose ryu.app.simple_switch_13
```

<img width="812" height="358" alt="inicia_controlador" src="https://github.com/user-attachments/assets/b0ee9ca7-1520-4649-93ff-c7afa356ac4f" />


### 5. Handshake Inicial (Ryu + Switch)

- OFPT_HELLO 
  Direção: Enviado por ambos (Switch $\leftrightarrow$ Controlador).
  Descrição: Primeira mensagem trocada no canal de controle. Utilizada para negociar a maior versão do protocolo suportada por ambas as partes (versão OpenFlow 1.3, identificada como 0x04).

- OFPT_FEATURES_REQUEST
  Direção: Controlador $\rightarrow$ Switch.
  Descrição: O controlador consulta as capacidades do hardware do switch, solicitando informações sobre portas, buffers e tabelas de fluxo.

- OFPT_FEATURES_REPLY
  Direção: Switch $\rightarrow$ Controlador.
  Descrição: O switch responde informando o seu Datapath ID (DPID único), quantidade de tabelas suportadas e recursos do plano de dados.

- OFPT_MULTIPART_REQUEST/REPLY
  Direção: Controlador $\leftrightarrow$ Switch.
  Descrição: Consulta de estatísticas e descrição detalhada do estado das interfaces físicas (s1-eth1, s1-eth2, s1-eth3), verificando velocidades, endereços MAC das portas e estados de link.

<img width="694" height="173" alt="image" src="https://github.com/user-attachments/assets/35abfb63-04ce-4900-85ad-98ed8452f1a9" />


### 6. No Mininet, testar a comunicação entre h1 e h2:
```
mininet> h1 ping -c 1 h2
```

O teste obtém resposta com sucesso (0% de perda de pacotes), apresentando um tempo RTT (Round-Trip Time) ligeiramente mais elevado no primeiro pacote devido ao tempo necessário para o switch consultar o controlador e gravar a nova regra de encaminhamento.


* **`OFPT_PACKET_IN` (Type 10) - Requisição ARP:**
  * **Origem/Destino SDN:** Switch `s1` -> Controlador Ryu.
  * **Descrição:** Como a tabela de fluxos local do switch está vazia, o comutador intercepta o pacote de requisição ARP de `h1` (buscando o MAC de `h2`) e o encaminha encapsulado ao Ryu.
  * **Análise do Payload:** No Wireshark, ao expandir `OpenFlow Protocol 1.3` -> `OFPT_PACKET_IN` -> `Packet Data` -> `Address Resolution Protocol`, observam-se os endereços `Sender IP: 10.0.0.1` e `Target IP: 10.0.0.2`.

* **`OFPT_PACKET_OUT` (Type 13) - Inundação (Flood):**
  * **Origem/Destino SDN:** Controlador Ryu -> Switch `s1`.
  * **Descrição:** O Ryu aprende a porta de origem do host `h1` (Porta 1), mas por ainda não conhecer a localização do host `h2`, ordena que o switch envie a requisição ARP em *flood* para todas as outras portas ativas.

* **`OFPT_PACKET_IN` (Type 10) - Resposta ARP:**
  * **Origem/Destino SDN:** Switch `s1` -> Controlador Ryu.
  * **Descrição:** O host `h2` responde ao ARP. O switch intercepta o *ARP Reply* e envia novo `PACKET_IN` ao Ryu, permitindo que o controlador aprenda que o MAC de `h2` está conectado à Porta 2.

* **`OFPT_FLOW_MOD` (Type 14) - Instalação de Regra:**
  * **Origem/Destino SDN:** Controlador Ryu -> Switch `s1`.
  * **Descrição:** O Ryu envia uma instrução `FLOW_MOD` gravando uma entrada na tabela de fluxos (*Flow Table*) do switch `s1`. A regra associa o MAC de destino de `h2` à ação de saída para a porta física correspondente, garantindo o chaveamento direto dos pacotes ICMP subsequentes.

 <img width="512" height="131" alt="h1_h2_pingOK" src="https://github.com/user-attachments/assets/cf522a30-6168-4e95-a229-17545dcafbbb" />

 <img width="557" height="111" alt="image" src="https://github.com/user-attachments/assets/468100d4-262c-4918-9f01-714a40a2af7c" /> 


 ## 🔍 Etapa 6: Verificação da Tabela de Fluxos (Item 8)

Após a comunicação inicial entre `h1` e `h2`, as regras instruídas pelo controlador Ryu ficam gravadas localmente na memória do switch OpenvSwitch. Para inspecionar essas entradas, utiliza-se a ferramenta de linha de comandos `ovs-ofctl`.

### 7. Tabela de fluxo
No terminal do sistema operativo, foi executado o seguinte comando, utilizando a flag `-O OpenFlow13` para forçar a compatibilidade com a versão correta do protocolo:

```
sudo ovs-ofctl dump-flows s1 -O OpenFlow13
```

A captura do terminal exibe três regras (fluxos) instaladas na table=0 do switch s1: 

* Regras Aprendidas (Tráfego de Dados L2):

- Fluxo para h1: Uma regra com priority=1 que instrui: todo o tráfego que entrar pela porta 2 (in_port="s1-eth2") com origem no MAC de h2 deve ser encaminhado para a porta 1 (actions=output:"s1-eth1").

- Fluxo para h2: Uma regra simétrica com priority=1 que instrui: todo o tráfego que entrar pela porta 1 (in_port="s1-eth1") com origem no MAC de h1 deve ser encaminhado para a porta 2 (actions=output:"s1-eth2").

* Regra Padrão (Table-Miss Flow):

- Uma regra com priority=0 (a prioridade mais baixa).

- Ação: actions=CONTROLLER:65535.

- Explicação: Esta é a regra de fail-secure que garante o funcionamento da rede SDN. Se um pacote chegar ao switch e não fizer match com nenhuma regra específica (como as de prioridade 1 acima), ele aciona esta regra padrão que encapsula   o pacote num PACKET_IN e o envia para a porta do Controlador.


 <img width="881" height="110" alt="tabela_Fluxos" src="https://github.com/user-attachments/assets/9a146a1e-337f-49fd-9ecc-4a67b4759cce" />


 

