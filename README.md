# Análise Comparativa de Modelos de Propagação Eletromagnética no Simulador NS-3

Este repositório documenta os procedimentos e resultados da atividade
prática de simulação de redes computacionais, focada na avaliação do
impacto de distintos modelos de propagação física sobre o desempenho de
redes sem fio padrão **IEEE 802.11n** em topologia **Ad-Hoc**.\
As simulações foram executadas utilizando o simulador de eventos
discretos **Network Simulator 3 (NS-3)**.

A metodologia integra algoritmos em **C++**, automação em **Bash** e
análise de dados em **Python**, permitindo a geração de visualizações
estatísticas robustas.

## 📋 Objetivos do Estudo

O objetivo central é analisar a correlação entre:

-   **Potência do Sinal Recebido (RSS)**
-   **Throughput**
-   **Distância euclidiana** entre transmissor e receptor

Foram avaliados **cinco modelos de propagação** para observar sua
resiliência e comportamento sob diferentes condições teóricas e
empíricas.

### 📡 Modelos de Propagação Avaliados

-   **FriisPropagationLossModel (Espaço Livre)**
-   **FixedRssLossModel (Controle)**
-   **ThreeLogDistancePropagationLossModel**
-   **TwoRayGroundPropagationLossModel**
-   **NakagamiPropagationLossModel**

## 🛠️ Metodologia e Ferramentas

-   **NS-3 (v3.42)**
-   **Bash Script**
-   **Python (Pandas & Matplotlib)**
-   **Docker**

## 📊 Análise dos Resultados

Gráficos gerados:

-   Throughput vs Distância
-   RSS vs Distância
-   Scatter Plot
-   Comparativo por Distância
-   Limiares de Interrupção
