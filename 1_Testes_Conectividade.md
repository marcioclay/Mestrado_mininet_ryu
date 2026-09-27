

 ---- ## 📸 Demonstração Prática e Resultados (Etapa 2)

### 1. Acesso Remoto à Máquina Virtual via SSH
Conexão efetuada através do Windows PowerShell para a máquina virtual do Mininet (`mininet@x.y.z.w`).

![Acesso SSH à VM do Mininet](./imagens/0_ssh.png)

---

### 2. Inicialização da Topologia 

Execução do script Python (`topologia.py`), criando a infraestrutura com **11 hosts** (`h1` a `h11`), **4 switches OpenFlow** (`s1` a `s4`), controlador local por omissão (`c0`) e enlaces configurados com restrições de largura de banda e atraso (`TCLink`) em https://github.com/marcioclay/Mestrado_mininet_ryu/blob/main/topologia.py. 

![Inicialização da Topologia](./imagens/1_criar_topologia.png)

---

### 3. Mapeamento de Interfaces e Teste de Conectividade (`pingAll`)
Exibição do mapeamento físico das portas de cada switch ligado aos respetivos hosts e verificação da comunicação total da rede.
* **Resultado do Ping:** `0% dropped (110/110 received)`, confirmando comutação de Layer 2 totalmente funcional entre todos os nós.

![Mapeamento de Portas e PingAll](./imagens/2_mapa_conectividade.png)

---

### 4. Avaliação de Largura de Banda (`iperf`)
Medição da taxa de transferência TCP entre o host `h1` e todos os restantes hosts da rede (`h2` a `h11`).
* **Resultado:** Vazão útil média constante entre **9.42 Mbits/sec** e **9.57 Mbits/sec**, perfeitamente alinhada com o limite teórico de $10\text{ Mbps}$ estipulado nos enlaces de acesso, considerando o *overhead* dos cabeçalhos das camadas TCP/IP.

![Teste de Banda iperf](./imagens/3_iperf.png)
