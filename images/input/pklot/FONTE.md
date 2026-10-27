# Origem e condições de uso das imagens

As imagens desta pasta são uma **amostra** do **PKLot — A Robust Dataset for
Parking Lot Classification**, produzido pelo Vision, Robotics and Imaging
Group (VRI) da Universidade Federal do Paraná (UFPR).

- **Página oficial:** https://web.inf.ufpr.br/vri/databases/parking-lot-database/
- **Arquivo completo:** https://www.inf.ufpr.br/vri/databases/PKLot.tar.gz (≈ 4,9 GB)
- **Licença:** Creative Commons Attribution 4.0 (CC BY 4.0) —
  https://creativecommons.org/licenses/by/4.0/
- **Citação:**
  ALMEIDA, P. R. L.; OLIVEIRA, L. S.; BRITTO JR., A. S.; SILVA JR., E. J.;
  KOERICH, A. L. *PKLot — A robust dataset for parking lot classification*.
  Expert Systems with Applications, v. 42, n. 11, p. 4937–4949, 2015.

## Por que a amostra está versionada aqui

A licença CC BY 4.0 permite a redistribuição com atribuição. Por isso
versionamos apenas as **30 imagens efetivamente usadas nos experimentos da
M2** (≈ 11 MB), para que o repositório seja reproduzível sem exigir o
download de 4,9 GB. O dataset completo **não** é versionado: quem quiser
reproduzir a seleção ou ampliá-la deve obtê-lo na origem.

## Como obter o dataset completo

```bash
curl -L -o PKLot.tar.gz https://www.inf.ufpr.br/vri/databases/PKLot.tar.gz
tar -xzf PKLot.tar.gz
```

As imagens completas com a anotação ficam em `PKLot/PKLot/<local>/<clima>/<data>/`,
em pares `<timestamp>.jpg` + `<timestamp>.xml`. (A pasta `PKLot/PKLotSegmented/`
contém recortes já segmentados por vaga; **não** a utilizamos, porque o recorte
das vagas é uma das etapas que o nosso pipeline implementa.)

## Estrutura desta amostra

| Pasta | Local | Imagens | Vagas anotadas | Uso |
|---|---|---|---|---|
| `ajuste/` | PUCPR | 6 | 597 | ajuste dos parâmetros e do limiar de decisão |
| `avaliacao/` | PUCPR | 12 | 1200 | avaliação na mesma cena, em datas disjuntas das de ajuste |
| `avaliacao_cruzada/` | UFPR04 + UFPR05 | 12 | 407 | estacionamentos nunca vistos no ajuste, com outra câmera, ângulo e escala |

Os arquivos foram renomeados para `<local>_<clima>_<data>_<hora>.jpg`, de modo
que o nome funcione como identificador nas tabelas de `results/`. O conteúdo
dos arquivos `.jpg` e `.xml` não foi alterado.

Os critérios de seleção e o protocolo experimental estão em
[`docs/relatorio_m2.md`](../../../docs/relatorio_m2.md).
