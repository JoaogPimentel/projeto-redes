# 🛰️ Monitoramento de Rede em Tempo Real

Este projeto é uma aplicação web desenvolvida com **Flask** e **JavaScript (Chart.js)** para monitoramento de métricas de rede em tempo real usando os protocolos **UDP** e **TCP**.

## 📋 Funcionalidades

- Escolha entre os protocolos **UDP** ou **TCP**
- Coleta e exibição das métricas:
  - 📶 **Latência**
  - 🌐 **Jitter**
  - 🚀 **Throughput (Taxa de Transmissão)**
  - ❌ **Perda de Pacotes**
- Visualização gráfica em tempo real usando **Chart.js**
- Backend assíncrono com comunicação cliente-servidor contínua

## 🗂️ Estrutura do Projeto
Projeto Redes/
│
├── static/
│ └── index.html # Interface Web com Dashboard
│
├── main.py # Servidor Flask com lógica de rede
├── README.md # Documentação do projeto
└── venv/ # Ambiente virtual Python

## ▶️ Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/JoaogPimentel/projeto-redes.git
cd projeto-redes

python -m venv venv
venv\Scripts\activate

pip install flask

python main.py

```
## Participantes

- Aloysio Felipe Saad Silva (@AloysioSaad)
- João Gabriel de Souza Pimentel (@JoaogPimentel)
- Lucas Ardelino Alvez da Silva (@Lucas172UFF)
- Pedro Piaes Rodrigues (@pedropiaesrodrigues)
