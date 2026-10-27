"""
Exemplo minimo de execucao do pipeline da M2 sobre uma unica imagem.

Entrada : caminho de uma imagem .jpg da amostra (o .xml de mesmo nome, com a
          geometria das vagas, precisa estar na mesma pasta).
Saida   : contagem de veiculos e taxa de ocupacao no terminal, mais uma
          imagem anotada em images/results/.

Uso:
    python src/contar_vagas.py images/input/pklot/avaliacao/PUCPR_Rainy_2012-10-11_08_46_33.jpg
    python src/contar_vagas.py <imagem> --config C1_bordas --limiar 0.0752
"""

import argparse
from pathlib import Path

import cv2

import pipeline
import pklot


def main():
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument("imagem", help="caminho da imagem .jpg a processar")
    analisador.add_argument(
        "--config",
        default=pipeline.CONFIGURACAO_PADRAO,
        choices=sorted(pipeline.CONFIGURACOES),
        help="configuracao do pipeline (padrao: %(default)s)",
    )
    analisador.add_argument(
        "--limiar",
        type=float,
        default=pipeline.LIMIAR_PADRAO,
        help="limiar de decisao sobre o descritor (padrao: %(default)s)",
    )
    argumentos = analisador.parse_args()

    caminho = Path(argumentos.imagem)
    config = pipeline.CONFIGURACOES[argumentos.config]

    linhas = pipeline.processar_imagem(caminho, config)
    pipeline.decidir(linhas, config, argumentos.limiar)
    resultado = pipeline.contar(linhas)

    referencia = sum(linha["referencia"] for linha in linhas)
    acertos = sum(linha["predito"] == linha["referencia"] for linha in linhas)

    print(f"Imagem              : {pklot.identificador(caminho)}")
    print(f"Configuracao        : {config.nome}")
    print(f"Descritor / limiar  : {config.descritor} >= {argumentos.limiar}")
    print(f"Vagas monitoradas   : {resultado['vagas_monitoradas']}")
    print(f"Veiculos detectados : {resultado['veiculos_detectados']}")
    print(f"Taxa de ocupacao    : {resultado['taxa_ocupacao']:.1%}")
    print(f"Referencia (anotada): {referencia} veiculos "
          f"(erro = {resultado['veiculos_detectados'] - referencia:+d})")
    print(f"Acuracia por vaga   : {acertos / len(linhas):.1%}")

    # imagem anotada: verde = vaga classificada como ocupada, azul = vazia
    img = pklot.carregar_imagem(caminho)
    vagas = {vaga.id: vaga for vaga in pklot.ler_vagas(caminho)}
    for linha in linhas:
        cor = (0, 200, 0) if linha["predito"] else (200, 120, 0)
        pontos = cv2.boxPoints(vagas[linha["vaga"]].retangulo).astype(int)
        cv2.drawContours(img, [pontos], 0, cor, 2)

    destino = (
        pklot.RAIZ_PROJETO
        / "images"
        / "results"
        / f"contagem_{pklot.identificador(caminho)}.png"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(destino), img)
    print(f"Imagem anotada      : {destino.relative_to(pklot.RAIZ_PROJETO)}")


if __name__ == "__main__":
    main()
