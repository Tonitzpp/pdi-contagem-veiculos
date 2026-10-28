# Contagem de Veículos em Estacionamentos a partir de Imagens Aéreas

Projeto aplicado longitudinal da disciplina de Processamento de Imagens.
**Estágio atual: M2 — implementação parcial executável, com resultados medidos.**

## Integrantes
- Toni Tison Zamparetti
- Gustavo Oliveira

---

## 1. Problema e contexto

Contar veículos em estacionamentos de grande porte manualmente ou com sensores
por vaga é caro e difícil de escalar. Este projeto investiga como técnicas
clássicas de Processamento Digital de Imagens podem, a partir de **uma única
imagem aérea do estacionamento**, decidir vaga a vaga se ela está ocupada e
produzir daí a **contagem de veículos**.

Aplicação: apoio de baixo custo à gestão de estacionamentos e eventos, a partir
de uma câmera fixa instalada em prédio vizinho (ou sobrevoos de drone), sem
instalar sensores em cada vaga.

## 2. Objetivo

Implementar e avaliar um pipeline de PDI que receba uma imagem aérea de
estacionamento e a geometria das vagas monitoradas, e produza o número de
veículos estacionados, com erro medido contra uma referência anotada. A **taxa
de ocupação** é saída secundária, derivada da contagem.

## 3. Entradas e saídas

```text
Entrada:  imagem aérea JPEG do estacionamento (1280 x 720, RGB)
        + geometria das vagas monitoradas (configuração do local)

Saída:    número de veículos estacionados          <- saída principal
        + taxa de ocupação (derivada)
        + imagem anotada com a decisão de cada vaga
        + tabelas CSV com descritores e métricas de erro
```

A geometria das vagas é tratada como **configuração do local**, marcada uma vez
na instalação da câmera. O rótulo `occupied` das anotações é usado **apenas**
como referência para medir o erro, nunca como entrada do processamento.

## 4. Pipeline implementado

```text
imagem aérea + geometria das vagas
   ↓
recorte retificado de cada vaga (warp de perspectiva, 64x64)
   ↓
pré-processamento (cinza + CLAHE + suavização gaussiana)
   ↓
segmentação (bordas de Canny)  →  morfologia (fechamento)
   ↓
análise de componentes conexas  →  4 descritores por vaga
   ↓
decisão ocupada / vazia por limiar
   ↓
contagem de veículos (+ taxa de ocupação)
```

Etapas, parâmetros e justificativas em
[`docs/relatorio_m2.md`](docs/relatorio_m2.md), seção 5.

## 5. Dados

**PKLot — A Robust Dataset for Parking Lot Classification** (VRI/UFPR), licença
**CC BY 4.0**. Imagens de câmera fixa em edifício, com vista aérea do
estacionamento e anotação por vaga (retângulo rotacionado + ocupada/vazia).

A amostra usada — **30 imagens, 2 204 vagas anotadas** — está versionada em
[`images/input/pklot/`](images/input/pklot/), com atribuição e instruções de
obtenção em [`images/input/pklot/FONTE.md`](images/input/pklot/FONTE.md). O
dataset completo (≈ 4,9 GB) **não** é versionado.

| Conjunto | Local | Imagens | Vagas | Papel |
|---|---|---:|---:|---|
| `ajuste/` | PUCPR | 6 | 597 | ajustar parâmetros e limiar de decisão |
| `avaliacao/` | PUCPR | 12 | 1 200 | mesma cena, datas disjuntas das de ajuste |
| `avaliacao_cruzada/` | UFPR04 + UFPR05 | 12 | 407 | estacionamentos nunca vistos no ajuste |

> Na M1 o dataset previsto era o CARPK. A troca, e as demais respostas ao
> feedback da M1, estão na seção 2 de
> [`docs/relatorio_m2.md`](docs/relatorio_m2.md).

## 6. Estágio atual

**Implementado e medido:** recorte retificado, pré-processamento, segmentação,
morfologia, componentes conexas, descritores, decisão, contagem e taxa de
ocupação; protocolo com conjuntos disjuntos por data e por local; comparação
controlada entre três configurações; análise de casos de sucesso e falha.

**Resultado da melhor configuração** (C2, desvio padrão de intensidade):

| Indicador | Avaliação (1 200 vagas) | Avaliação cruzada (407 vagas) |
|---|---:|---:|
| Acurácia por vaga | 91,3 % | **95,1 %** |
| MAE de contagem por imagem | 8,08 | **1,50** |
| RMSE de contagem por imagem | 10,91 | **1,91** |
| Erro relativo médio | 50,5 %¹ | **6,9 %** |
| Falsos positivos / negativos | 86 / 19 | 14 / 6 |

¹ inflado por duas imagens quase vazias; ver seção 5.4 do relatório.

**Pendente para a M3:** classificador sobre o vetor de descritores, descritores
de textura contra os falsos positivos em piso texturizado, e detecção
automática da grade de vagas. Plano com responsáveis na seção 8 do relatório.

## 7. Organização do repositório

```text
pdi-contagem-veiculos/
├── README.md
├── requirements.txt
├── docs/
│   ├── proposta.md            # proposta da M1, com as revisões da M2 marcadas
│   └── relatorio_m2.md        # relatório parcial da M2  <- documento principal
├── src/
│   ├── pklot.py               # leitura da amostra: imagens, anotações, recorte da vaga
│   ├── pipeline.py            # etapas de PDI e configurações comparadas
│   ├── experimento_m2.py      # executa os experimentos, grava tabelas e figuras
│   ├── contar_vagas.py        # exemplo mínimo: 1 imagem -> contagem + taxa
│   └── experimento_contagem.py  # experimento da M1, mantido como registro
├── images/
│   ├── input/pklot/           # amostra do dataset + FONTE.md
│   └── results/               # figuras geradas
└── results/                   # tabelas geradas (CSV)
```

## 8. Tecnologias e ambiente

Python 3.12 · OpenCV (`opencv-python-headless`) · NumPy · Matplotlib.
Versões testadas: `opencv-python-headless 5.0.0.93`, `numpy 2.5.4`,
`matplotlib 3.11.2`; mínimas em [`requirements.txt`](requirements.txt).

```bash
# em Debian/Ubuntu, o módulo venv vem em pacote separado:
#   sudo apt install python3.12-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 9. Como reproduzir

As imagens já estão no repositório; nenhum download é necessário. Rode a partir
da raiz do projeto.

### 9.1 Exemplo mínimo — uma imagem

```bash
python src/contar_vagas.py images/input/pklot/avaliacao/PUCPR_Rainy_2012-10-11_08_46_33.jpg
```

Saída esperada:

```text
Imagem              : PUCPR_Rainy_2012-10-11_08_46_33
Configuracao        : C2 — desvio padrao de intensidade
Descritor / limiar  : desvio_intensidade >= 0.16
Vagas monitoradas   : 100
Veiculos detectados : 94
Taxa de ocupacao    : 94.0%
Referencia (anotada): 94 veiculos (erro = +0)
Acuracia por vaga   : 100.0%
Imagem anotada      : images/results/contagem_PUCPR_Rainy_2012-10-11_08_46_33.png
```

Outras configurações e limiares:

```bash
python src/contar_vagas.py <imagem> --config C1_bordas --limiar 0.0752
```

### 9.2 Experimentos completos da M2

```bash
python src/experimento_m2.py
```

Executa as três configurações sobre os três conjuntos, ajusta o limiar no
conjunto de ajuste, aplica-o sem reajuste aos demais e grava:

- `results/m2_resumo.csv` — indicadores por configuração e conjunto
- `results/m2_metricas_por_imagem.csv` — erro de contagem imagem a imagem
- `results/m2_descritores.csv` — um registro por vaga, por configuração
- `images/results/m2_*.png` — figuras usadas no relatório

### 9.3 Experimento da M1 (registro)

```bash
python src/experimento_contagem.py
```

## 10. Resultados

Figuras e análise em [`docs/relatorio_m2.md`](docs/relatorio_m2.md), seção 6.
Resumo da comparação controlada:

| Configuração | O que muda | Acurácia (avaliação) | MAE | Acurácia (cruzada) | MAE |
|---|---|---:|---:|---:|---:|
| C1 — densidade de borda (Canny + fechamento) | descritor vindo da segmentação | 80,4 % | 18,25 | 80,6 % | 6,58 |
| **C2 — desvio padrão de intensidade** | descritor fotométrico | **91,3 %** | **8,08** | **95,1 %** | **1,50** |
| C3 — densidade de borda sem fechamento | C1 sem morfologia | 85,8 % | 12,92 | 81,6 % | 6,25 |

Dois achados: o descritor fotométrico separa as classes bem melhor que a
densidade de bordas, e o fechamento morfológico **piora** o resultado — ele
consolida a textura do piso mais que a silhueta do veículo.

## 11. Vídeo

- **Vídeo da M1:** https://youtu.be/90XMToKZbqo

## 12. Documentação adicional

- [`docs/relatorio_m2.md`](docs/relatorio_m2.md) — relatório parcial da M2:
  resposta ao feedback, dados, protocolo, pipeline, experimentos, limitações,
  plano da M3, contribuições e declaração de uso de IA generativa.
- [`docs/proposta.md`](docs/proposta.md) — proposta da M1, com as revisões da M2
  marcadas.
- [`images/input/pklot/FONTE.md`](images/input/pklot/FONTE.md) — origem, licença
  e obtenção das imagens.
