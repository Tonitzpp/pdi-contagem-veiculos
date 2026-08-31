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