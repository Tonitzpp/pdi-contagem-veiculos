# Contagem de Veículos em Estacionamentos a partir de Imagens Aéreas

## Integrantes
- Toni Tison Zamparetti
- Gustavo Oliveira

## 1. Problema investigado

Contar veículos em estacionamentos de grande porte (shoppings, aeroportos,
eventos) manualmente ou por câmeras de nível do solo é inviável em escala —
requer múltiplas câmeras, sofre com oclusão entre carros e não dá uma visão
geral da ocupação. Este projeto investiga como técnicas de Processamento
Digital de Imagens podem **detectar e contar veículos automaticamente** a
partir de uma única imagem aérea (drone ou satélite) do estacionamento.

Descrição detalhada em [`docs/proposta.md`](docs/proposta.md).

## 2. Contexto de aplicação

Apoio à gestão de estacionamentos e eventos: estimar ocupação em tempo
quase real a partir de sobrevoos periódicos de drone (ou imagens de
satélite atualizadas), sem depender de sensores por vaga. Útil também para
planejamento urbano e dimensionamento de vagas.

## 3. Objetivo geral

Desenvolver um pipeline de PDI que, a partir de uma imagem aérea de um
estacionamento, **detecte e conte o número de veículos presentes**,
evoluindo, ao longo do semestre, para **estimar a taxa de ocupação** (vagas
ocupadas vs. vagas totais visíveis na imagem).

## 4. Visão resumida da solução proposta

Pipeline clássico de PDI: pré-processamento → realce de contraste →
detecção de veículos (segmentação por forma/blob ou detecção de bordas) →
contagem → (evolução futura: estimativa de ocupação por vaga). Detalhes em
[`docs/proposta.md`](docs/proposta.md#pipeline-preliminar).

## 5. Conjunto/origem das imagens

Dataset alvo: **CARPK Dataset** (Car Parking lot dataset), criado
especificamente para contagem/detecção de veículos em imagens aéreas
capturadas por drone, com anotações (bounding boxes) por veículo. Ver
seção 8 da proposta para detalhes de licença e forma de obtenção. Nesta
fase M1, os experimentos preliminares usam uma **imagem sintética gerada
localmente** (`src/experimento_contagem.py`) simulando veículos vistos de
cima, como substituta temporária para validar o pipeline técnico antes de
o dataset real estar versionado no repositório.

## 6. Estágio atual do projeto

**M1 — definição do problema e prova de conceito técnica.**

Já realizado:
- Definição e delimitação do problema.
- Pipeline preliminar desenhado (com alternativas de detecção).
- Experimento preliminar de detecção/contagem rodando sobre imagem de
  exemplo (ver `images/results/`).
- Identificação do dataset definitivo e plano de obtenção.

Ainda não realizado (esperado para M2/M3):
- Download e organização do CARPK Dataset real.
- Validação da contagem com métricas quantitativas (erro absoluto médio
  frente à contagem de referência do dataset).
- Extensão para estimativa de ocupação por vaga (M3).

## 7. Organização do repositório

```text
projeto-contagem-aerea/
├── README.md
├── docs/
│   └── proposta.md          # proposta técnica detalhada
├── images/
│   ├── input/                # imagens de entrada (exemplo/dataset)
│   └── results/               # saídas dos experimentos
├── src/
│   └── experimento_contagem.py   # pipeline preliminar (detecção + contagem)
├── notebooks/                 # (reservado para exploração futura)
├── requirements.txt
└── .gitignore
```

## 8. Tecnologias previstas / já utilizadas

- Python 3.12
- OpenCV (`opencv-python-headless`)
- scikit-image
- NumPy / SciPy
- Matplotlib (visualização)
- (Futuro, M2/M3) scikit-learn ou um detector leve pré-treinado, como
  alternativa a ser comparada com o pipeline clássico

## 9. Como reproduzir o experimento preliminar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/experimento_contagem.py
```

O script gera uma imagem sintética simulando um estacionamento visto de
cima, aplica o pipeline de detecção e salva o resultado em
`images/results/experimento_contagem_veiculos.png`.

## 10. Vídeo da M1



## 11. Documentação adicional

- Proposta técnica completa: [`docs/proposta.md`](docs/proposta.md)
- Registro de uso de IA generativa: seção 9 da proposta.

