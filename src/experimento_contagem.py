"""
Experimento preliminar - M1
Projeto: Contagem de veiculos em estacionamentos a partir de imagens aereas

Como o dataset definitivo (CARPK) ainda nao foi baixado, este script usa
uma imagem sintetica de um estacionamento visto de cima para validar o
pipeline de deteccao e contagem. Detalhes e discussao dos resultados em
docs/proposta.md.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os


def gerar_imagem_sintetica_estacionamento(largura=500, altura=400, n_veiculos=30, seed=7):
    rng = np.random.default_rng(seed)

    fundo = rng.integers(55, 70, (altura, largura), dtype=np.uint8)
    img = cv2.cvtColor(fundo, cv2.COLOR_GRAY2BGR).astype(np.float64)

    for x in range(30, largura - 30, 45):
        cv2.line(img, (x, 20), (x, altura - 20), (200, 200, 200), 2)

    cores_veiculo = [
        (40, 40, 180), (180, 40, 40), (40, 140, 40),
        (200, 200, 200), (30, 30, 30), (140, 140, 40),
    ]

    centros_usados = []
    tentativas = 0
    while len(centros_usados) < n_veiculos and tentativas < n_veiculos * 20:
        tentativas += 1
        cx = rng.integers(35, largura - 35)
        cy = rng.integers(35, altura - 35)

        muito_perto = any(np.hypot(cx - ox, cy - oy) < 18 for ox, oy in centros_usados)
        if muito_perto:
            continue

        centros_usados.append((cx, cy))
        largura_veic = rng.integers(22, 30)
        altura_veic = rng.integers(12, 16)
        angulo = rng.integers(0, 180)
        cor = cores_veiculo[rng.integers(0, len(cores_veiculo))]

        retangulo = (
            (float(cx), float(cy)),
            (float(largura_veic), float(altura_veic)),
            float(angulo),
        )
        pontos = cv2.boxPoints(retangulo).astype(np.intp)
        cv2.fillConvexPoly(img, pontos, cor)

    img = np.clip(img, 0, 255).astype(np.uint8)
    return img, len(centros_usados)


def carregar_imagem_exemplo():
    return gerar_imagem_sintetica_estacionamento()


def pre_processamento(img_bgr):
    """Reducao de ruido + realce de contraste (CLAHE no canal de luminancia)."""
    img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(img_lab)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_eq = clahe.apply(l)

    img_lab_eq = cv2.merge([l_eq, a, b])
    img_realcada = cv2.cvtColor(img_lab_eq, cv2.COLOR_LAB2BGR)
    img_realcada = cv2.GaussianBlur(img_realcada, (3, 3), 0)
    return img_realcada


def detectar_candidatos(img_realcada):
    """
    Segmentacao por limiar no canal de saturacao (HSV). Uma primeira
    versao usava deteccao por bordas (Canny), mas falhava porque as
    marcacoes de vaga se conectavam aos veiculos apos o fechamento
    morfologico (ver docs/proposta.md, secao 7).
    """
    img_hsv = cv2.cvtColor(img_realcada, cv2.COLOR_BGR2HSV)
    saturacao = img_hsv[:, :, 1]

    _, mask = cv2.threshold(saturacao, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_limpa = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_limpa = cv2.morphologyEx(mask_limpa, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask_limpa


def filtrar_por_forma(mask, area_min=150, area_max=800, aspecto_max=4.0):
    """Filtra candidatos por area e razao de aspecto (descarta marcacoes de vaga)."""
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidatos_validos = []
    for c in contornos:
        area = cv2.contourArea(c)
        if area < area_min or area > area_max:
            continue

        retangulo = cv2.minAreaRect(c)
        (_, _), (w, h), _ = retangulo
        lado_maior = max(w, h)
        lado_menor = max(min(w, h), 1e-3)
        aspecto = lado_maior / lado_menor

        if aspecto > aspecto_max:
            continue

        candidatos_validos.append(retangulo)

    return candidatos_validos


def salvar_visualizacao(img_original, mask, candidatos, caminho_saida):
    img_com_deteccoes = img_original.copy()
    for retangulo in candidatos:
        pontos = cv2.boxPoints(retangulo).astype(np.intp)
        cv2.drawContours(img_com_deteccoes, [pontos], 0, (0, 255, 0), 2)

    img_original_rgb = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
    img_deteccoes_rgb = cv2.cvtColor(img_com_deteccoes, cv2.COLOR_BGR2RGB)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    axes[0].imshow(img_original_rgb)
    axes[0].set_title("Imagem de entrada (exemplo)")
    axes[0].axis("off")

    axes[1].imshow(mask, cmap="gray")
    axes[1].set_title("Máscara de candidatos (saturação HSV + morfologia)")
    axes[1].axis("off")

    axes[2].imshow(img_deteccoes_rgb)
    axes[2].set_title(f"Veículos detectados após filtragem - N = {len(candidatos)}")
    axes[2].axis("off")

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    print(f"Visualizacao salva em: {caminho_saida}")


def main():
    img, n_veiculos_gerados = carregar_imagem_exemplo()
    
    os.makedirs("images/input", exist_ok=True)
    cv2.imwrite("images/input/exemplo_estacionamento_sintetico.png", img)

    img_pre = pre_processamento(img)
    mask = detectar_candidatos(img_pre)

    contornos_brutos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Contornos brutos (sem filtragem): {len(contornos_brutos)}")

    candidatos = filtrar_por_forma(mask)
    print(f"Veiculos detectados apos filtragem: {len(candidatos)} (de {n_veiculos_gerados} gerados)")
    print(
        "Limitacao observada: veiculos de baixa saturacao (branco/cinza/preto) "
        "nao sao bem capturados por este criterio. Ver docs/proposta.md, secao 7.2."
    )

    salvar_visualizacao(img, mask, candidatos, "images/results/experimento_contagem_veiculos.png")


if _name_ == "_main_":
    main()