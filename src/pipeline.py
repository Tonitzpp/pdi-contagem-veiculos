"""
Pipeline de PDI da M2.

Para cada vaga:
    recorte retificado -> pre-processamento (cinza + CLAHE + suavizacao)
    -> segmentacao (Canny) -> morfologia (fechamento)
    -> componentes conexas -> descritores -> decisao por limiar

A saida do sistema e a contagem de veiculos da imagem; a taxa de ocupacao e
derivada dela. Os limiares sao ajustados por src/experimento_m2.py sobre o
conjunto de ajuste. Justificativa dos parametros: docs/relatorio_m2.md.
"""

from collections import namedtuple

import cv2
import numpy as np

import pklot

Configuracao = namedtuple(
    "Configuracao",
    ["nome", "usar_clahe", "canny_min", "canny_max", "fechamento", "descritor"],
)

CONFIGURACOES = {
    "C1_bordas": Configuracao(
        nome="C1 — densidade de borda (Canny + fechamento)",
        usar_clahe=True,
        canny_min=50,
        canny_max=150,
        fechamento=True,
        descritor="densidade_borda",
    ),
    "C2_textura": Configuracao(
        nome="C2 — desvio padrao de intensidade",
        usar_clahe=True,
        canny_min=50,
        canny_max=150,
        fechamento=True,
        descritor="desvio_intensidade",
    ),
    "C3_sem_morfologia": Configuracao(
        nome="C3 — densidade de borda (Canny sem fechamento)",
        usar_clahe=True,
        canny_min=50,
        canny_max=150,
        fechamento=False,
        descritor="densidade_borda",
    ),
}

CONFIGURACAO_PADRAO = "C2_textura"

# limiar da configuracao padrao, ajustado no conjunto de ajuste
LIMIAR_PADRAO = 0.1600

ELEMENTO_ESTRUTURANTE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
AREA_MINIMA_COMPONENTE = 0.01  # fracao do patch


def preprocessar(patch_bgr, usar_clahe=True):
    """Cinza + realce de contraste local + suavizacao."""
    cinza = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2GRAY)
    if usar_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        cinza = clahe.apply(cinza)
    return cv2.GaussianBlur(cinza, (3, 3), 0)


def segmentar(cinza, config):
    """Devolve (mascara do Canny, mascara apos o fechamento morfologico)."""
    bordas = cv2.Canny(cinza, config.canny_min, config.canny_max)
    if not config.fechamento:
        return bordas, bordas
    fechada = cv2.morphologyEx(
        bordas, cv2.MORPH_CLOSE, ELEMENTO_ESTRUTURANTE, iterations=1
    )
    return bordas, fechada


def analisar_componentes(mascara):
    """Rotula as componentes conexas e devolve (rotulos, areas em fracao)."""
    quantidade, rotulos, estatisticas, _ = cv2.connectedComponentsWithStats(mascara, 8)
    if quantidade <= 1:
        return rotulos, np.array([], dtype=float)

    areas = estatisticas[1:, cv2.CC_STAT_AREA] / float(mascara.size)
    return rotulos, np.sort(areas[areas >= AREA_MINIMA_COMPONENTE])[::-1]


def descrever(cinza, mascara, areas):
    """
    densidade_borda     fracao de pixels marcados na mascara (0-1)
    area_maior_regiao   area da maior componente conexa, em fracao do patch (0-1)
    n_componentes       componentes acima da area minima (contagem)
    desvio_intensidade  desvio padrao do patch realcado, normalizado (0-1)
    """
    return {
        "densidade_borda": float(np.count_nonzero(mascara)) / mascara.size,
        "area_maior_regiao": float(areas[0]) if areas.size else 0.0,
        "n_componentes": int(areas.size),
        "desvio_intensidade": float(np.std(cinza)) / 255.0,
    }


def processar_vaga(img_bgr, retangulo, config, guardar_intermediarias=False):
    patch = pklot.recortar_vaga(img_bgr, retangulo)
    cinza = preprocessar(patch, config.usar_clahe)
    bordas, mascara = segmentar(cinza, config)
    rotulos, areas = analisar_componentes(mascara)

    resultado = descrever(cinza, mascara, areas)
    if guardar_intermediarias:
        resultado["_intermediarias"] = {
            "patch": patch,
            "cinza": cinza,
            "bordas": bordas,
            "mascara": mascara,
            "rotulos": rotulos,
        }
    return resultado


def processar_imagem(caminho_jpg, config):
    """Um registro por vaga, com descritores e rotulo de referencia."""
    img = pklot.carregar_imagem(caminho_jpg)
    nome = pklot.identificador(caminho_jpg)

    linhas = []
    for vaga in pklot.ler_vagas(caminho_jpg):
        descritores = processar_vaga(img, vaga.retangulo, config)
        descritores.update(imagem=nome, vaga=vaga.id, referencia=vaga.ocupada)
        linhas.append(descritores)
    return linhas


def decidir(linhas, config, limiar):
    for linha in linhas:
        linha["predito"] = int(linha[config.descritor] >= limiar)
    return linhas


def contar(linhas):
    """Saida do sistema: contagem de veiculos e, derivada dela, a ocupacao."""
    total = len(linhas)
    detectados = sum(linha["predito"] for linha in linhas)
    return {
        "vagas_monitoradas": total,
        "veiculos_detectados": detectados,
        "taxa_ocupacao": detectados / total if total else 0.0,
    }
