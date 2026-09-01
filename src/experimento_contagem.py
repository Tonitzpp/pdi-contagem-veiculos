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


def main():
    # Apenas gera e salva a imagem sintética por enquanto
    img, n_veiculos_gerados = carregar_imagem_exemplo()
    
    # Simula a criação do arquivo na pasta de input
    import os
    os.makedirs("images/input", exist_ok=True)
    cv2.imwrite("images/input/exemplo_estacionamento_sintetico.png", img)
    print(f"Imagem sintetica gerada com {n_veiculos_gerados} veiculos.")


if __name__ == "__main__":
    main()