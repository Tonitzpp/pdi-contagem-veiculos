"""
Experimentos da M2.

Executa o pipeline em tres configuracoes, ajusta o limiar de decisao somente
no conjunto de ajuste e aplica-o sem reajuste aos conjuntos de avaliacao.

  E1  qual descritor separa melhor vaga ocupada de vaga vazia: a densidade de
      borda vinda da segmentacao (C1) ou o desvio de intensidade (C2)?
  E2  o fechamento morfologico melhora a decisao (C1) ou so infla a resposta
      do piso (C3)?

Uso:
    python src/experimento_m2.py

Saidas: results/m2_*.csv e images/results/m2_*.png
"""

import csv

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import pipeline
import pklot

RAIZ = pklot.RAIZ_PROJETO
PASTA_TABELAS = RAIZ / "results"
PASTA_FIGURAS = RAIZ / "images" / "results"

CAMPOS_DESCRITORES = [
    "densidade_borda",
    "area_maior_regiao",
    "n_componentes",
    "desvio_intensidade",
]


def extrair(config):
    dados = {}
    for conjunto in pklot.CONJUNTOS:
        linhas = []
        for caminho in pklot.listar_imagens(conjunto):
            linhas.extend(pipeline.processar_imagem(caminho, config))
        dados[conjunto] = linhas
    return dados


def ajustar_limiar(linhas, config):
    """Limiar de maior acuracia no conjunto de ajuste, varrendo 200 quantis."""
    valores = np.array([linha[config.descritor] for linha in linhas])
    referencia = np.array([linha["referencia"] for linha in linhas])

    melhor_limiar, melhor_acuracia = float(valores.min()), 0.0
    for limiar in np.quantile(valores, np.linspace(0.01, 0.99, 200)):
        acuracia = ((valores >= limiar).astype(int) == referencia).mean()
        if acuracia > melhor_acuracia:
            melhor_limiar, melhor_acuracia = float(limiar), float(acuracia)
    return melhor_limiar, melhor_acuracia


def metricas_por_imagem(linhas):
    por_imagem = {}
    for linha in linhas:
        por_imagem.setdefault(linha["imagem"], []).append(linha)

    resultado = []
    for imagem in sorted(por_imagem):
        vagas = por_imagem[imagem]
        referencia = sum(v["referencia"] for v in vagas)
        detectados = sum(v["predito"] for v in vagas)
        total = len(vagas)
        erro = detectados - referencia
        resultado.append(
            {
                "imagem": imagem,
                "vagas_monitoradas": total,
                "veiculos_referencia": referencia,
                "veiculos_detectados": detectados,
                "erro_contagem": erro,
                # indefinido quando a imagem nao tem nenhum veiculo
                "erro_relativo": round(abs(erro) / referencia, 4) if referencia else "",
                "taxa_referencia": round(referencia / total, 4),
                "taxa_detectada": round(detectados / total, 4),
                "erro_taxa_pp": round(erro / total * 100, 2),
                "acuracia_vagas": round(
                    sum(v["predito"] == v["referencia"] for v in vagas) / total, 4
                ),
            }
        )
    return resultado


def metricas_agregadas(linhas):
    predito = np.array([linha["predito"] for linha in linhas])
    referencia = np.array([linha["referencia"] for linha in linhas])

    vp = int(((predito == 1) & (referencia == 1)).sum())
    fp = int(((predito == 1) & (referencia == 0)).sum())
    fn = int(((predito == 0) & (referencia == 1)).sum())

    por_imagem = metricas_por_imagem(linhas)
    erros = np.array([m["erro_contagem"] for m in por_imagem], dtype=float)
    relativos = [m["erro_relativo"] for m in por_imagem if m["erro_relativo"] != ""]

    return {
        "n_vagas": len(linhas),
        "n_imagens": len(por_imagem),
        "acuracia_vagas": round(float((predito == referencia).mean()), 4),
        "precisao": round(vp / (vp + fp), 4) if vp + fp else 0.0,
        "revocacao": round(vp / (vp + fn), 4) if vp + fn else 0.0,
        "falsos_positivos": fp,
        "falsos_negativos": fn,
        "mae_contagem": round(float(np.abs(erros).mean()), 2),
        "rmse_contagem": round(float(np.sqrt((erros ** 2).mean())), 2),
        "vies_contagem": round(float(erros.mean()), 2),
        "erro_relativo_medio": round(float(np.mean(relativos)), 4) if relativos else "",
        "n_imagens_erro_relativo": len(relativos),
        "erro_medio_taxa_pp": round(
            float(np.mean([abs(m["erro_taxa_pp"]) for m in por_imagem])), 2
        ),
    }


def testar_combinacao(linhas_ajuste, conjuntos):
    """
    Teste exploratorio: "ocupada se desvio_intensidade >= T1 E
    area_maior_regiao >= T2", com os dois limiares buscados em grade no
    conjunto de ajuste. Mede se vale trocar o limiar unico por um
    classificador sobre o vetor de descritores na M3.
    """
    def valores(linhas, campo):
        return np.array([linha[campo] for linha in linhas])

    desvio = valores(linhas_ajuste, "desvio_intensidade")
    area = valores(linhas_ajuste, "area_maior_regiao")
    referencia = valores(linhas_ajuste, "referencia")

    melhor = (0.0, float(desvio.min()), float(area.min()))
    for limiar_desvio in np.quantile(desvio, np.linspace(0.02, 0.98, 60)):
        for limiar_area in np.quantile(area, np.linspace(0.02, 0.98, 60)):
            predito = (desvio >= limiar_desvio) & (area >= limiar_area)
            acuracia = (predito.astype(int) == referencia).mean()
            if acuracia > melhor[0]:
                melhor = (float(acuracia), float(limiar_desvio), float(limiar_area))

    _, limiar_desvio, limiar_area = melhor
    resultados = []
    for nome_conjunto, linhas in conjuntos.items():
        copia = [dict(linha) for linha in linhas]
        for linha in copia:
            linha["predito"] = int(
                linha["desvio_intensidade"] >= limiar_desvio
                and linha["area_maior_regiao"] >= limiar_area
            )
        indicadores = metricas_agregadas(copia)
        resultados.append(
            {
                "configuracao": "C4_combinado",
                "descricao": "C4 (exploratorio) — desvio_intensidade E area_maior_regiao",
                "descritor": f"desvio_intensidade>={limiar_desvio:.4f} & "
                f"area_maior_regiao>={limiar_area:.4f}",
                "limiar": round(limiar_desvio, 4),
                "conjunto": nome_conjunto,
                **indicadores,
            }
        )
        print(
            f"  {nome_conjunto:18s} acuracia={indicadores['acuracia_vagas']:.3f} "
            f"MAE={indicadores['mae_contagem']:5.2f}"
        )
    return resultados


# ----------------------------------------------------------------------
# Figuras
# ----------------------------------------------------------------------


def figura_etapas_pipeline(config):
    caminho = pklot.listar_imagens("ajuste")[1]
    img = pklot.carregar_imagem(caminho)
    vagas = pklot.ler_vagas(caminho)

    # vaga mediana de cada classe, para mostrar um caso tipico e nao um extremo
    escolhidas = []
    for rotulo in (1, 0):
        candidatas = [
            (pipeline.processar_vaga(img, v.retangulo, config), v)
            for v in vagas
            if v.ocupada == rotulo
        ]
        candidatas.sort(key=lambda par: par[0][config.descritor])
        vaga = candidatas[len(candidatas) // 2][1]
        escolhidas.append(
            (vaga, pipeline.processar_vaga(img, vaga.retangulo, config, True))
        )

    titulos = [
        "1. Recorte retificado\n(64x64)",
        "2. Cinza + CLAHE\n+ suavizacao",
        "3. Segmentacao\n(Canny)",
        "4. Morfologia\n(fechamento)",
        "5. Componentes\nconexas",
    ]
    fig, eixos = plt.subplots(2, 5, figsize=(14, 6))

    for linha, (vaga, resultado) in enumerate(escolhidas):
        etapas = resultado["_intermediarias"]
        rotulos = etapas["rotulos"]
        colorido = cv2.applyColorMap(
            (rotulos * (255 // max(rotulos.max(), 1))).astype(np.uint8), cv2.COLORMAP_JET
        )
        imagens = [
            cv2.cvtColor(etapas["patch"], cv2.COLOR_BGR2RGB),
            etapas["cinza"],
            etapas["bordas"],
            etapas["mascara"],
            cv2.cvtColor(colorido, cv2.COLOR_BGR2RGB),
        ]
        for coluna, (imagem, titulo) in enumerate(zip(imagens, titulos)):
            eixo = eixos[linha][coluna]
            eixo.imshow(imagem, cmap=None if imagem.ndim == 3 else "gray")
            eixo.axis("off")
            if linha == 0:
                eixo.set_title(titulo, fontsize=10)

        estado = "OCUPADA" if vaga.ocupada else "VAZIA"
        eixos[linha][0].axis("on")
        eixos[linha][0].set_xticks([])
        eixos[linha][0].set_yticks([])
        eixos[linha][0].set_ylabel(estado)
        eixos[linha][4].text(
            1.05,
            0.5,
            f"vaga {vaga.id} ({estado})\n"
            f"densidade_borda = {resultado['densidade_borda']:.3f}\n"
            f"area_maior_regiao = {resultado['area_maior_regiao']:.3f}\n"
            f"n_componentes = {resultado['n_componentes']}\n"
            f"desvio_intensidade = {resultado['desvio_intensidade']:.3f}",
            transform=eixos[linha][4].transAxes,
            fontsize=9,
            va="center",
        )

    fig.suptitle(
        f"Saidas intermediarias do pipeline — {pklot.identificador(caminho)}", fontsize=12
    )
    fig.tight_layout(rect=(0, 0, 0.82, 0.96))
    destino = PASTA_FIGURAS / "m2_etapas_pipeline.png"
    fig.savefig(destino, dpi=140)
    plt.close(fig)
    return destino


def figura_histogramas(linhas_ajuste, limiares):
    fig, eixos = plt.subplots(1, 2, figsize=(12, 4.5))

    for eixo, descritor in zip(eixos, ["densidade_borda", "desvio_intensidade"]):
        vazias = [l[descritor] for l in linhas_ajuste if l["referencia"] == 0]
        ocupadas = [l[descritor] for l in linhas_ajuste if l["referencia"] == 1]
        faixa = (min(vazias + ocupadas), max(vazias + ocupadas))
        eixo.hist(vazias, bins=40, range=faixa, alpha=0.6, label="vaga vazia")
        eixo.hist(ocupadas, bins=40, range=faixa, alpha=0.6, label="vaga ocupada")
        eixo.axvline(
            limiares[descritor],
            color="k",
            linestyle="--",
            label=f"limiar ajustado = {limiares[descritor]:.3f}",
        )
        eixo.set_xlabel(descritor)
        eixo.set_ylabel("numero de vagas")
        eixo.set_title(descritor)
        eixo.legend(fontsize=8)

    fig.suptitle(
        "Distribuicao dos descritores no conjunto de ajuste (597 vagas)", fontsize=12
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    destino = PASTA_FIGURAS / "m2_histogramas_descritores.png"
    fig.savefig(destino, dpi=140)
    plt.close(fig)
    return destino


def figura_overlay(conjunto, nome_imagem, linhas, sufixo):
    caminho = next(
        c for c in pklot.listar_imagens(conjunto) if pklot.identificador(c) == nome_imagem
    )
    img = pklot.carregar_imagem(caminho)
    vagas = {v.id: v for v in pklot.ler_vagas(caminho)}

    cores = {  # (predito, referencia) -> BGR
        (1, 1): (0, 200, 0),
        (0, 0): (200, 120, 0),
        (1, 0): (0, 140, 255),
        (0, 1): (0, 0, 255),
    }
    contagem = {chave: 0 for chave in cores}

    visual = img.copy()
    for linha in linhas:
        if linha["imagem"] != nome_imagem:
            continue
        chave = (linha["predito"], linha["referencia"])
        contagem[chave] += 1
        pontos = cv2.boxPoints(vagas[linha["vaga"]].retangulo).astype(np.intp)
        cv2.drawContours(visual, [pontos], 0, cores[chave], 2)

    referencia = contagem[(1, 1)] + contagem[(0, 1)]
    detectados = contagem[(1, 1)] + contagem[(1, 0)]
    total = sum(contagem.values())

    fig, eixo = plt.subplots(figsize=(12, 7))
    eixo.imshow(cv2.cvtColor(visual, cv2.COLOR_BGR2RGB))
    eixo.axis("off")
    eixo.set_title(
        f"{nome_imagem}\n"
        f"referencia = {referencia} veiculos | detectado = {detectados} "
        f"(erro = {detectados - referencia:+d}) | "
        f"taxa de ocupacao {detectados / total:.0%} vs {referencia / total:.0%}\n"
        f"verde = ocupada correta | azul = vazia correta | "
        f"laranja = falso positivo ({contagem[(1, 0)]}) | "
        f"vermelho = falso negativo ({contagem[(0, 1)]})",
        fontsize=10,
    )
    fig.tight_layout()
    destino = PASTA_FIGURAS / f"m2_overlay_{sufixo}.png"
    fig.savefig(destino, dpi=140)
    plt.close(fig)
    return destino


def figura_comparacao(resumo):
    configuracoes = list(pipeline.CONFIGURACOES)
    conjuntos = list(pklot.CONJUNTOS)
    largura = 0.25
    posicoes = np.arange(len(conjuntos))

    fig, eixos = plt.subplots(1, 2, figsize=(12, 4.5))
    for indice, chave in enumerate(configuracoes):
        deslocamento = (indice - 1) * largura
        eixos[0].bar(
            posicoes + deslocamento,
            [resumo[(chave, c)]["acuracia_vagas"] for c in conjuntos],
            largura,
            label=chave,
        )
        eixos[1].bar(
            posicoes + deslocamento,
            [resumo[(chave, c)]["mae_contagem"] for c in conjuntos],
            largura,
            label=chave,
        )

    eixos[0].set_ylim(0.70, 1.0)  # eixo cortado: a diferenca fica legivel
    for eixo, titulo, rotulo in (
        (eixos[0], "Acuracia por vaga (maior e melhor)", "acuracia"),
        (eixos[1], "Erro absoluto medio de contagem (menor e melhor)", "veiculos"),
    ):
        eixo.set_xticks(posicoes)
        eixo.set_xticklabels(conjuntos, fontsize=9)
        eixo.set_title(titulo, fontsize=11)
        eixo.set_ylabel(rotulo)
        eixo.legend(fontsize=8)

    fig.tight_layout()
    destino = PASTA_FIGURAS / "m2_comparacao_configuracoes.png"
    fig.savefig(destino, dpi=140)
    plt.close(fig)
    return destino


def gravar_csv(caminho, campos, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"  tabela: {caminho.relative_to(RAIZ)}")


def main():
    PASTA_TABELAS.mkdir(exist_ok=True)
    PASTA_FIGURAS.mkdir(parents=True, exist_ok=True)

    dados, resumo, limiares = {}, {}, {}
    linhas_descritores, linhas_por_imagem, linhas_resumo = [], [], []

    for chave, config in pipeline.CONFIGURACOES.items():
        print(f"\n[{chave}] {config.nome}")
        conjuntos = extrair(config)

        limiar, acuracia_ajuste = ajustar_limiar(conjuntos["ajuste"], config)
        limiares[chave] = limiar
        print(
            f"  limiar ajustado sobre '{config.descritor}' = {limiar:.4f} "
            f"(acuracia no ajuste = {acuracia_ajuste:.3f})"
        )

        for nome_conjunto, linhas in conjuntos.items():
            pipeline.decidir(linhas, config, limiar)
            indicadores = metricas_agregadas(linhas)
            resumo[(chave, nome_conjunto)] = indicadores
            print(
                f"  {nome_conjunto:18s} acuracia={indicadores['acuracia_vagas']:.3f} "
                f"MAE={indicadores['mae_contagem']:5.2f} "
                f"RMSE={indicadores['rmse_contagem']:5.2f} "
                f"FP={indicadores['falsos_positivos']:4d} "
                f"FN={indicadores['falsos_negativos']:4d}"
            )

            linhas_resumo.append(
                {
                    "configuracao": chave,
                    "descricao": config.nome,
                    "descritor": config.descritor,
                    "limiar": round(limiar, 4),
                    "conjunto": nome_conjunto,
                    **indicadores,
                }
            )
            linhas_por_imagem.extend(
                {"configuracao": chave, "conjunto": nome_conjunto, **metrica}
                for metrica in metricas_por_imagem(linhas)
            )
            linhas_descritores.extend(
                {"configuracao": chave, "conjunto": nome_conjunto, **linha}
                for linha in linhas
            )

        dados[chave] = conjuntos

    print("\n[C4_combinado] teste exploratorio: textura E area da maior regiao")
    linhas_resumo.extend(
        testar_combinacao(dados["C1_bordas"]["ajuste"], dados["C1_bordas"])
    )

    print("\nTabelas:")
    gravar_csv(
        PASTA_TABELAS / "m2_descritores.csv",
        ["configuracao", "conjunto", "imagem", "vaga", "referencia", "predito"]
        + CAMPOS_DESCRITORES,
        linhas_descritores,
    )
    gravar_csv(
        PASTA_TABELAS / "m2_metricas_por_imagem.csv",
        [
            "configuracao",
            "conjunto",
            "imagem",
            "vagas_monitoradas",
            "veiculos_referencia",
            "veiculos_detectados",
            "erro_contagem",
            "erro_relativo",
            "taxa_referencia",
            "taxa_detectada",
            "erro_taxa_pp",
            "acuracia_vagas",
        ],
        linhas_por_imagem,
    )
    gravar_csv(
        PASTA_TABELAS / "m2_resumo.csv",
        [
            "configuracao",
            "descricao",
            "descritor",
            "limiar",
            "conjunto",
            "n_imagens",
            "n_vagas",
            "acuracia_vagas",
            "precisao",
            "revocacao",
            "falsos_positivos",
            "falsos_negativos",
            "mae_contagem",
            "rmse_contagem",
            "vies_contagem",
            "erro_relativo_medio",
            "n_imagens_erro_relativo",
            "erro_medio_taxa_pp",
        ],
        linhas_resumo,
    )

    print("\nFiguras:")
    padrao = pipeline.CONFIGURACOES[pipeline.CONFIGURACAO_PADRAO]
    conjuntos_padrao = dados[pipeline.CONFIGURACAO_PADRAO]
    avaliacao = conjuntos_padrao["avaliacao"]
    por_imagem = metricas_por_imagem(avaliacao)

    saidas = [
        figura_etapas_pipeline(padrao),
        figura_histogramas(
            dados["C1_bordas"]["ajuste"],
            {
                "densidade_borda": limiares["C1_bordas"],
                "desvio_intensidade": limiares["C2_textura"],
            },
        ),
        figura_overlay(
            "avaliacao",
            min(por_imagem, key=lambda m: abs(m["erro_contagem"]))["imagem"],
            avaliacao,
            "sucesso",
        ),
        figura_overlay(
            "avaliacao",
            max(por_imagem, key=lambda m: abs(m["erro_contagem"]))["imagem"],
            avaliacao,
            "falha",
        ),
        figura_overlay(
            "ajuste",
            min(
                metricas_por_imagem(conjuntos_padrao["ajuste"]),
                key=lambda m: m["erro_contagem"],
            )["imagem"],
            conjuntos_padrao["ajuste"],
            "falsos_negativos",
        ),
        figura_overlay(
            "avaliacao_cruzada",
            max(
                metricas_por_imagem(conjuntos_padrao["avaliacao_cruzada"]),
                key=lambda m: abs(m["erro_contagem"]),
            )["imagem"],
            conjuntos_padrao["avaliacao_cruzada"],
            "cruzada",
        ),
        figura_comparacao(resumo),
    ]
    for destino in saidas:
        print(f"  figura: {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
