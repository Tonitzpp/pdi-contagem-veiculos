# Roteiro do vídeo — M2

**Duração alvo:** ~10 minutos · **YouTube, não listado** · link no README, seção 11.
**Participantes:** Toni Tison Zamparetti (T) e Gustavo Oliveira (G).

## Antes de gravar

- [ ] Abrir o repositório no GitHub em uma aba e o VS Code na raiz do projeto.
- [ ] Deixar abertas as figuras de `images/results/` (dá para arrastar todas de
      uma vez) e o arquivo `results/m2_resumo.csv`.
- [ ] Terminal já na raiz do projeto, com o venv ativado
      (`source venv/bin/activate`), fonte ampliada.
- [ ] Apagar as saídas antes de gravar, para a execução ao vivo gerar tudo do
      zero: `rm -rf results images/results/m2_*.png images/results/contagem_*.png`
- [ ] Cada um aparece na câmera e se identifica ao assumir a fala (requisito de
      participação identificável).
- [ ] Os dois comandos são rápidos (5 s e 0,2 s), então dá para rodar ao vivo.

---

## Bloco 1 — Abertura (0:00–0:45) · **T e G**

**Tela:** página do repositório no GitHub.

- **T:** "Oi, eu sou o Toni Tison Zamparetti."
- **G:** "E eu sou o Gustavo Oliveira. Este é o vídeo da M2 do nosso projeto:
  contagem de veículos em estacionamentos a partir de imagens aéreas."
- **T:** Em uma frase, o problema: *contar veículos em estacionamentos grandes
  com câmera, sem sensor por vaga*. A saída principal é a **contagem**; a taxa
  de ocupação é derivada dela.
- **G:** O que o vídeo vai mostrar: o que mudou desde a M1, os dados, o pipeline
  rodando de verdade, a comparação experimental, as falhas e o plano da M3.

---

## Bloco 2 — Evolução desde a M1 e resposta ao feedback (0:45–2:30) · **T**

**Tela:** `docs/relatorio_m2.md`, seção 2 (tabela de resposta ao feedback).

- Situação na M1: pipeline rodava sobre **uma imagem sintética**, com retângulos
  coloridos; detectava 17 de 30. Tínhamos dataset planejado (CARPK), mas não
  obtido.
- **Os 5 direcionamentos e o que fizemos** — passar a tabela mostrando cada um:
  1. *Obter o CARPK.* **Adotamos outra solução:** o CARPK só sai mediante
     formulário de solicitação, o que impede documentar obtenção reproduzível em
     repositório público. Trocamos pelo **PKLot da UFPR**: licença **CC BY 4.0**
     explícita, download direto por URL e — decisivo — **anotação vaga a vaga**.
     O objetivo do direcionamento, sair do sintético para um dataset real e
     licenciado, foi cumprido.
  2. *Abandonar a taxa de ocupação como requisito principal.* **Adotado:** a
     contagem virou a saída principal e o alvo das métricas; a ocupação é
     derivada.
  3. *Dividir por local/cena.* **Adotado** — e é a mudança mais importante;
     detalho no próximo bloco.
  4. *Medir MAE, RMSE e erro relativo.* **Adotado**, estão todos no CSV.
  5. *Manter a baseline clássica antes do detector aprendido.* **Adotado:** a M2
     é 100 % clássica, o classificador fica para a M3.
- **Prioridade imediata do professor** — rodar em dados reais e dizer quais
  hipóteses do cenário sintético caem. Mostrar a tabela da seção 2.1 e citar
  duas: (a) no sintético os carros tinham cores saturadas, no real a maioria é
  branca, prata ou preta — por isso **abandonamos o critério de saturação da
  M1**; (b) no sintético o fundo era asfalto homogêneo, no real tem grama,
  paralelepípedo e cascalho — e é daí que vem o nosso principal modo de falha.

---

## Bloco 3 — Dados e protocolo (2:30–4:00) · **T**

**Tela:** `images/input/pklot/` no VS Code, depois `FONTE.md`, depois a seção 4
do relatório. Abrir uma imagem do PUCPR e uma do UFPR04 para mostrar a diferença
de ângulo.

- PKLot: câmera fixa em edifício, vista aérea, 1280 × 720, XML por imagem com
  retângulo rotacionado de cada vaga + rótulo ocupada/vazia.
- **Licença CC BY 4.0** — mostrar o `FONTE.md`: por isso versionamos as **30
  imagens usadas** (11 MB) com atribuição, e **não** o dataset completo de 4,9 GB,
  que tem instrução de download documentada.
- **Importante deixar claro:** a geometria das vagas é tratada como
  *configuração do local* — marcada uma vez na instalação da câmera. O rótulo
  `occupied` é usado **só como referência de avaliação**, nunca entra no
  processamento.
- **Os três conjuntos** (mostrar a tabela da seção 4):

  | Conjunto | Local | Imagens | Vagas |
  |---|---|---:|---:|
  | ajuste | PUCPR | 6 | 597 |
  | avaliação | PUCPR, datas disjuntas | 12 | 1 200 |
  | avaliação cruzada | UFPR04 + UFPR05 | 12 | 407 |

- Dois níveis de separação: **por data** (imagens do mesmo dia são quase
  idênticas) e **por local** (o conjunto cruzado troca câmera, ângulo, escala e
  estacionamento inteiros). O conjunto cruzado é o que mede generalização de
  verdade — foi exatamente o direcionamento 3.
- A amostra vai de **0 % a 100 % de ocupação** de propósito: imagens vazias são
  as únicas em que falso positivo aparece sem nada para mascarar. Tem até uma
  imagem **noturna sob chuva**.

---

## Bloco 4 — Pipeline e saídas intermediárias (4:00–5:30) · **G**

**Tela:** diagrama do pipeline (seção 5 do relatório), depois `src/pipeline.py`,
depois a figura `m2_etapas_pipeline.png`.

- Mostrar o diagrama e descrever o fluxo em uma passada: recorte retificado →
  cinza + CLAHE + suavização → Canny → fechamento → componentes conexas →
  descritores → decisão → contagem.
- **Por que recortar a vaga antes de tudo:** resolve de uma vez dois problemas
  da M1 — a morfologia fundindo veículo com marcação de solo, e veículos colados
  virando um blob só. O *warp* de perspectiva deixa todas as vagas comparáveis
  apesar de posição, ângulo e escala diferentes.
- Abrir `src/pipeline.py` e mostrar que cada etapa é uma função: `preprocessar`,
  `segmentar`, `analisar_componentes`, `descrever`, `decidir`, `contar`.
- **Justificar dois parâmetros** (mostra que entendemos o que estamos usando):
  - **CLAHE com blocos 4 × 4:** vagas da mesma imagem estão sob luz muito
    diferente (sol, sombra, chuva); o realce **local** é o que torna um limiar
    único comparável entre elas.
  - **Escala 0,85 no recorte:** o retângulo anotado pega uma faixa de asfalto e
    encosta no vizinho; encolher 15 % concentra o recorte no interior da vaga.
- **Figura 1 (`m2_etapas_pipeline.png`)** — passar coluna por coluna: recorte,
  pré-processamento, Canny, fechamento, componentes. Comparar as duas linhas:
  vaga ocupada dá malha densa de bordas (`densidade_borda = 0,176`); vaga vazia
  dá só a borda do canteiro (`0,075`). **Apontar já aqui** que o fechamento
  engrossou justamente a borda do canteiro — é a deixa para o experimento 2.
- Listar os 4 descritores e dizer o que cada um mede.

---

## Bloco 5 — Execução ao vivo (5:30–6:45) · **G**

**Tela:** terminal.

1. Exemplo mínimo, uma imagem:
   ```bash
   python src/contar_vagas.py images/input/pklot/avaliacao/PUCPR_Rainy_2012-10-11_08_46_33.jpg
   ```
   Ler a saída em voz alta: 100 vagas monitoradas, 94 detectados, taxa 94 %,
   referência 94, **erro zero**. Abrir a imagem anotada que ele gerou em
   `images/results/`.

2. Experimentos completos (roda em ~5 s):
   ```bash
   python src/experimento_m2.py
   ```
   Enquanto roda / ao terminar: mostrar que ele imprime as três configurações
   nos três conjuntos e gravou as tabelas em `results/` e as figuras em
   `images/results/`. Abrir `results/m2_resumo.csv` e mostrar as colunas MAE,
   RMSE, erro relativo, precisão e revocação — os indicadores que o professor
   pediu.

> Dizer explicitamente: **não há valor escrito à mão em lugar nenhum** — todo
> número do relatório sai desses CSVs.

---

## Bloco 6 — Os dois experimentos (6:45–8:15) · **G**

**Tela:** figuras `m2_histogramas_descritores.png` e
`m2_comparacao_configuracoes.png`, e as tabelas da seção 6 do relatório.

**Experimento 1 — qual descritor separa melhor?**
- O que muda: **só o descritor da decisão**. Todo o resto é idêntico, inclusive
  o jeito de escolher o limiar.
- Resultado: C1 (densidade de borda) 80,4 % na avaliação; C2 (desvio de
  intensidade) **91,3 %**. No cruzado, 80,6 % contra **95,1 %**. O MAE cai de
  18,3 para 8,1 e de 6,6 para 1,5.
- **Mostrar a Figura 2 e explicar o porquê:** no histograma da densidade de
  borda há uma **cauda longa de vagas vazias com densidade alta** — são as vagas
  sobre grama e paralelepípedo. A densidade de borda não distingue "estrutura de
  veículo" de "estrutura de piso". Como o limiar precisa ser baixo para pegar
  carro escuro, passa todo piso texturizado: **227 falsos positivos contra 8
  falsos negativos**.

**Experimento 2 — a morfologia ajuda?**
- O que muda: **só a presença do fechamento**.
- Resultado: **piora**. 80,4 % com fechamento contra 85,8 % sem; 64 falsos
  positivos a mais, e **nenhum** falso negativo recuperado.
- Explicar: as bordas do veículo já saem conectadas pelo Canny, então o
  fechamento acrescenta pouco a elas; já as bordas finas e paralelas do
  paralelepípedo ficam a poucos pixels umas das outras, e são justamente essas
  que o elemento 3 × 3 une. **A operação está sendo aplicada no lugar errado: o
  fundo se beneficia dela mais que o objeto.**
- Conclusão que levamos para a M3: morfologia só **depois** de uma segmentação
  que já separe veículo de piso.
- Mostrar a Figura 7: a ordem das configurações se mantém nos três conjuntos —
  não é acidente de uma partição.

---

## Bloco 7 — Falhas e limitações (8:15–9:15) · **T**

**Tela:** `m2_overlay_sucesso.png`, `m2_overlay_falha.png`,
`m2_overlay_falsos_negativos.png`, `m2_overlay_cruzada.png`.

- **Sucesso (Figura 3):** estacionamento lotado sob chuva, 94 de 94, acurácia
  100 %. Cenário favorável: veículo ocupa o recorte inteiro, vaga vazia é
  asfalto homogêneo.
- **Pior caso (Figura 4):** estacionamento **vazio**, referência 0, detectamos
  23. Todos falsos positivos, e **concentrados em dois lugares**: a fileira de
  **paralelepípedo** e as vagas cortadas pela **faixa de grama**. Esse é o modo
  de falha dominante, e era previsível pelo histograma.
- **Falha oposta (Figura 5):** erro −26. Os falsos negativos caem quase todos em
  **veículos escuros sob luz difusa de dia chuvoso** — superfície uniforme, sem
  brilho, variação abaixo do limiar. É a limitação da M1 reaparecendo em outra
  forma: ela é propriedade do problema, não do critério que usávamos antes.
- **Cruzada (Figura 6):** limiar ajustado no PUCPR aplicado sem reajuste no
  UFPR05 — outra câmera, outro ângulo. Pior caso do conjunto: erro de **4
  veículos**, e os falsos positivos caem em canteiros de concreto com vegetação
  e cascalho. Mesmo mecanismo.
- Citar as limitações honestas: só contamos veículos **nas vagas monitoradas**;
  a geometria das vagas ainda vem da anotação; a referência é dos autores do
  dataset e não foi auditada vaga a vaga.

---

## Bloco 8 — Plano da M3 e fechamento (9:15–10:00) · **T e G**

**Tela:** seção 8 do relatório (tabela do plano da M3).

- **G:** As três tarefas técnicas e por que cada uma vem do que medimos hoje:
  1. **Classificador** sobre os 4 descritores — porque testamos combinar dois
     descritores numa regra booleana e o ganho foi de só 0,2 ponto; a regra
     manual é o gargalo, não os descritores.
  2. **Descritores de textura** (LBP, textura direcional) — atacam diretamente o
     modo de falha dominante, o piso texturizado.
  3. **Detecção automática da grade de vagas** — é a etapa do problema que ainda
     não resolvemos; é também a de maior risco, e já está documentado o que
     fazemos se não funcionar.
- **T:** Ampliar a amostra para ≥ 60 imagens e avaliar por estacionamento
  separadamente. Mencionar a tabela de contribuições da seção 9.
- **Fechamento (ambos):** o que a M2 entrega — pipeline rodando de ponta a
  ponta, 2 204 vagas avaliadas, protocolo com separação por data e por local,
  dois experimentos controlados, e os números batendo entre relatório e CSV.
- Agradecer e encerrar.

---

## Checklist de requisitos do enunciado

| Requisito do vídeo | Bloco |
|---|---|
| Evolução desde a M1 | 2 |
| Dados | 3 |
| Pipeline implementado | 4 |
| Execução real | 5 |
| Saídas intermediárias | 4 |
| Comparação experimental | 6 |
| Limitações | 7 |
| Plano da M3 | 8 |
| Participação identificável de todos | 1 e ao longo |
