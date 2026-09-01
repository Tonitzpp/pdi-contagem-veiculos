# Proposta Técnica — M1
## Contagem de Veículos em Estacionamentos a partir de Imagens Aéreas

---

## 1. Problema

### 1.1 O que será investigado

Estacionamentos de grande porte (shoppings, aeroportos, campi, eventos)
precisam saber, com frequência, quantos veículos estão presentes em um
determinado momento, para gestão operacional, sinalização de vagas
disponíveis ou planejamento de eventos. A contagem manual (funcionário
percorrendo o local) ou por sensores individuais por vaga é cara e difícil
de escalar.

Este projeto investiga até que ponto técnicas de Processamento Digital de
Imagens conseguem **detectar e contar veículos automaticamente** a partir
de uma única imagem aérea (capturada por drone ou disponível via imagem de
satélite), e evoluir para uma **estimativa de ocupação** (vagas ocupadas
vs. vagas totais visíveis).

### 1.2 Por que envolve PDI

O problema depende diretamente de:

- **Realce de contraste**: veículos em estacionamentos aparecem com baixo
  contraste em relação ao asfalto, especialmente em cores escuras ou sob
  sombra.
- **Segmentação e detecção de blobs**: separar formas retangulares
  (veículos) do fundo (asfalto, marcações de vaga, vegetação).
- **Morfologia matemática**: separar veículos estacionados muito próximos
  uns dos outros (situação comum em estacionamentos lotados).
- **Geometria/orientação**: veículos aparecem em ângulos variados
  dependendo da disposição das vagas, o que exige que a detecção não
  dependa de uma orientação fixa.

### 1.3 Situação inicial e informação a ser produzida

**Entrada:** imagem aérea (vista de cima, drone ou satélite) de um
estacionamento, em RGB.

**Saída pretendida (evolutiva ao longo do semestre):**
- **M1/M2:** número total de veículos detectados na imagem + marcação
  visual de cada detecção.
- **M3:** taxa de ocupação do estacionamento (veículos detectados / total
  de vagas identificadas na imagem), com uma métrica de acerto sobre um
  conjunto de teste anotado.

---

## 2. Contexto de aplicação

O sistema não pretende substituir sensores de precisão por vaga em
aplicações críticas, mas servir como **apoio de baixo custo** para gestão
de estacionamentos de médio/grande porte: um sobrevoo periódico de drone
(ou uma imagem de satélite atualizada) seria suficiente para estimar
ocupação sem infraestrutura de sensores instalada em cada vaga.

Esse contexto é suficientemente concreto para definir critérios de sucesso
(comparação da contagem automática com a contagem de referência do
dataset) e compatível com o escopo de uma disciplina de graduação, sem a
pretensão de uso comercial imediato.

---

## 3. Objetivo

### Objetivo geral
Desenvolver um pipeline de PDI que, a partir de uma imagem aérea de um
estacionamento, detecte e conte os veículos presentes, evoluindo para uma
estimativa de taxa de ocupação.

### Objetivos específicos
1. Implementar um pipeline de pré-processamento robusto a variações de
   iluminação, sombra e contraste típicas de imagens aéreas.
2. Detectar veículos independentemente de sua orientação na imagem.
3. Separar veículos estacionados próximos/colados (situação de
   estacionamento cheio).
4. Validar a contagem automática contra a contagem de referência (ground
   truth) do CARPK Dataset, medindo erro absoluto médio.
5. (M2/M3) Identificar as vagas marcadas na imagem (quando visíveis) para
   calcular taxa de ocupação, não só contagem absoluta.
6. (M3) Comparar o pipeline clássico com uma alternativa mais robusta
   (ex.: um detector leve pré-treinado) e discutir os trade-offs.

---

## 4. Entrada e saída esperadas

```text
imagem aérea de estacionamento (RGB)
   ↓
pré-processamento (realce de contraste, redução de ruído)
   ↓
detecção de candidatos a veículo (segmentação / detecção de blobs)
   ↓
separação de veículos próximos (morfologia / watershed)
   ↓
filtragem por forma e tamanho (descarta ruído, marcações de solo)
   ↓
contagem de veículos ──────────────────► [M1/M2: saída principal]
   ↓
associação com vagas identificadas (M3)
   ↓
taxa de ocupação ──────────────────────► [M3: saída principal]
```

### Critérios de sucesso (verificáveis)
- **Contagem:** erro absoluto médio entre contagem automática e contagem
  de referência (anotações do CARPK), medido sobre um subconjunto de
  imagens de teste.
- **Ocupação (M3):** proporção de vagas corretamente classificadas como
  ocupadas/vazias, quando a segmentação de vagas for viável a partir das
  imagens disponíveis.

---