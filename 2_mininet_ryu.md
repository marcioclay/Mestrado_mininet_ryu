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
