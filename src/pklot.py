"""
Leitura da amostra do PKLot.

Cada imagem vem com um XML que descreve a geometria de cada vaga monitorada e
se ela estava ocupada. A geometria e tratada como configuracao do local; o
campo "occupied" e usado apenas como referencia de avaliacao.

Origem e licenca: images/input/pklot/FONTE.md
"""

from collections import namedtuple
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import numpy as np

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
RAIZ_AMOSTRA = RAIZ_PROJETO / "images" / "input" / "pklot"

CONJUNTOS = ("ajuste", "avaliacao", "avaliacao_cruzada")

# retangulo = ((cx, cy), (largura, altura), angulo), formato do cv2
Vaga = namedtuple("Vaga", ["id", "ocupada", "retangulo"])


def listar_imagens(conjunto):
    if conjunto not in CONJUNTOS:
        raise ValueError(f"conjunto deve ser um de {CONJUNTOS}, recebido: {conjunto!r}")
    return sorted((RAIZ_AMOSTRA / conjunto).glob("*.jpg"))


def identificador(caminho_jpg):
    return Path(caminho_jpg).stem


def ler_vagas(caminho_jpg):
    raiz = ET.parse(Path(caminho_jpg).with_suffix(".xml")).getroot()

    vagas = []
    for elemento in raiz.findall("space"):
        ocupada = elemento.get("occupied")
        retangulo = elemento.find("rotatedRect")
        if ocupada is None or retangulo is None:
            continue  # vaga sem rotulo: nao ha como avaliar

        centro = retangulo.find("center")
        tamanho = retangulo.find("size")
        angulo = retangulo.find("angle")
        vagas.append(
            Vaga(
                id=elemento.get("id"),
                ocupada=int(ocupada),
                retangulo=(
                    (float(centro.get("x")), float(centro.get("y"))),
                    (float(tamanho.get("w")), float(tamanho.get("h"))),
                    float(angulo.get("d")),
                ),
            )
        )
    return vagas


def carregar_imagem(caminho_jpg):
    img = cv2.imread(str(caminho_jpg))
    if img is None:
        raise FileNotFoundError(f"nao foi possivel ler a imagem: {caminho_jpg}")
    return img


def recortar_vaga(img_bgr, retangulo, lado=64, escala=0.85):
    """
    Recorta a vaga e a retifica para um quadrado `lado` x `lado` por
    transformacao de perspectiva, tornando todas as vagas comparaveis apesar
    de posicao, angulo e escala diferentes. `escala` < 1 encolhe o retangulo
    para reduzir o asfalto e os veiculos vizinhos que entram no recorte.
    """
    (centro, (largura, altura), angulo) = retangulo
    origem = cv2.boxPoints(
        (centro, (largura * escala, altura * escala), angulo)
    ).astype(np.float32)
    destino = np.array(
        [[0, lado - 1], [0, 0], [lado - 1, 0], [lado - 1, lado - 1]], dtype=np.float32
    )
    return cv2.warpPerspective(
        img_bgr, cv2.getPerspectiveTransform(origem, destino), (lado, lado)
    )
