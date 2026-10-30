"""Coleta a cobertura vegetal dos bairros de Curitiba a partir de imagens de satélite.

Uso:
    python scripts/coletar_cobertura.py                # atualiza o histórico do MapBiomas
    python scripts/coletar_cobertura.py --worldcover   # recalcula a cobertura de árvores (ESA WorldCover)

Só o pedaço de Curitiba de cada mapa é baixado (os arquivos são Cloud-Optimized
GeoTIFF), então cada ano leva poucos segundos.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

PASTA_DADOS = Path(__file__).resolve().parent.parent / "src" / "Dados-Bairros"
ARQ_BAIRROS = PASTA_DADOS / "bairros_curitiba.csv"
ARQ_HISTORICO = PASTA_DADOS / "historico_vegetacao.csv"
ARQ_CONTORNOS = PASTA_DADOS / "bairros_curitiba.geojson"
ARQ_FONTES = PASTA_DADOS / "fontes.json"

# MapBiomas, coleção de 10 m (imagens Sentinel-2)
MAPBIOMAS_BUCKET = "https://storage.googleapis.com/mapbiomas-public"
MAPBIOMAS_PASTA = "initiatives/brasil/lulc_10m/collection4/coverage/brazil_coverage/"
MAPBIOMAS_ARQUIVO = re.compile(r"brazil_coverage-col4_10m_(\d{4})\.tif$")
# Classes de vegetação da legenda do MapBiomas: formações florestais, savânicas,
# campestres e áreas úmidas, silvicultura, pastagem e mosaico de usos
MAPBIOMAS_VEGETACAO = [3, 4, 5, 6, 9, 11, 12, 15, 21, 49, 50]

# ESA WorldCover 10 m, versão 2021 (classe 10 = cobertura de árvores)
WORLDCOVER_URL = ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
                  "ESA_WorldCover_10m_2021_v200_S27W051_Map.tif")
WORLDCOVER_ARVORES = [10]

# Limites das conferências feitas antes de aceitar dados novos
MEDIA_CIDADE_MIN, MEDIA_CIDADE_MAX = 10, 60
VARIACAO_MAX_POR_ANO = 25  # pontos percentuais de um ano para o outro

GDAL = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
            GDAL_HTTP_MULTIRANGE="YES", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
            GDAL_HTTP_MAX_RETRY="5", GDAL_HTTP_RETRY_DELAY="2")


def carregar_contornos():
    with open(ARQ_CONTORNOS, encoding="utf-8") as f:
        feats = json.load(f)["features"]
    return [f["properties"]["nome"] for f in feats], [f["geometry"] for f in feats]


def listar_anos_mapbiomas():
    """Anos disponíveis no MapBiomas, lidos da listagem pública do bucket."""
    with urlopen(f"{MAPBIOMAS_BUCKET}/?prefix={MAPBIOMAS_PASTA}&delimiter=/", timeout=60) as r:
        xml = r.read().decode()
    chaves = re.findall(r"<Key>([^<]+)</Key>", xml)
    return sorted(int(m.group(1)) for k in chaves if (m := MAPBIOMAS_ARQUIVO.search(k)))


def porcentagem_por_bairro(url, classes, nomes, geoms):
    """Porcentagem da área de cada bairro coberta pelas classes informadas."""
    import numpy as np
    import rasterio
    from rasterio.features import rasterize
    from rasterio.warp import transform_bounds, transform_geom
    from rasterio.windows import Window, from_bounds

    coords = [c for g in geoms for anel in g["coordinates"] for c in anel]
    limites = (min(c[0] for c in coords), min(c[1] for c in coords),
               max(c[0] for c in coords), max(c[1] for c in coords))
    with rasterio.Env(**GDAL), rasterio.open(f"/vsicurl/{url}") as r:
        janela = from_bounds(*transform_bounds("EPSG:4326", r.crs, *limites), transform=r.transform)
        janela = janela.round_offsets().round_lengths().intersection(Window(0, 0, r.width, r.height))
        mapa = r.read(1, window=janela)
        ids = rasterize([(transform_geom("EPSG:4326", r.crs, g), i + 1) for i, g in enumerate(geoms)],
                        out_shape=mapa.shape, transform=r.window_transform(janela), fill=0, dtype="uint8")
    total = np.bincount(ids.ravel(), minlength=len(nomes) + 1)[1:]
    alvo = np.bincount(ids.ravel(), weights=np.isin(mapa, classes).ravel(), minlength=len(nomes) + 1)[1:]
    return pd.Series((alvo / total * 100).round(1), index=nomes)


def validar_ano(valores, anterior=None):
    """Lista de problemas encontrados nos dados de um ano (vazia quando está tudo certo)."""
    problemas = []
    if len(valores) != 75 or valores.isna().any():
        problemas.append(f"esperava 75 bairros com valor, recebi {valores.notna().sum()}")
    if ((valores < 0) | (valores > 100)).any():
        problemas.append("há valores fora do intervalo de 0% a 100%")
    if not MEDIA_CIDADE_MIN <= valores.mean() <= MEDIA_CIDADE_MAX:
        problemas.append(f"média da cidade fora do esperado: {valores.mean():.1f}%")
    if anterior is not None:
        variacao = (valores - anterior).abs()
        estranhos = variacao[variacao > VARIACAO_MAX_POR_ANO]
        if not estranhos.empty:
            problemas.append("variação acima de %d p.p. em: %s" % (
                VARIACAO_MAX_POR_ANO, ", ".join(f"{n} ({v:.1f})" for n, v in estranhos.items())))
    return problemas


def atualizar_historico(nomes, geoms):
    historico = pd.read_csv(ARQ_HISTORICO) if ARQ_HISTORICO.exists() else pd.DataFrame(columns=["NOME", "ano", "vegetacao"])
    ja_coletados = set(historico["ano"].astype(int))
    novos = [a for a in listar_anos_mapbiomas() if a not in ja_coletados]
    if not novos:
        print("Histórico já está atualizado.")
        return []

    for ano in novos:
        url = f"{MAPBIOMAS_BUCKET}/{MAPBIOMAS_PASTA}brazil_coverage-col4_10m_{ano}.tif"
        valores = porcentagem_por_bairro(url, MAPBIOMAS_VEGETACAO, nomes, geoms)
        anteriores = historico[historico["ano"] == ano - 1].set_index("NOME")["vegetacao"]
        problemas = validar_ano(valores, anteriores.reindex(valores.index) if not anteriores.empty else None)
        if problemas:
            sys.exit(f"Dados do MapBiomas {ano} recusados:\n- " + "\n- ".join(problemas))
        historico = pd.concat([historico, pd.DataFrame({"NOME": nomes, "ano": ano, "vegetacao": valores.values})])
        print(f"MapBiomas {ano}: média da cidade {valores.mean():.1f}%")

    historico = historico.sort_values(["ano", "NOME"]).astype({"ano": int})
    historico.to_csv(ARQ_HISTORICO, index=False)
    return novos


def atualizar_worldcover(nomes, geoms):
    valores = porcentagem_por_bairro(WORLDCOVER_URL, WORLDCOVER_ARVORES, nomes, geoms)
    problemas = validar_ano(valores)
    if problemas:
        sys.exit("Dados do WorldCover recusados:\n- " + "\n- ".join(problemas))
    pd.DataFrame({"NOME": valores.index, "cobertura_arborea": valores.values}).to_csv(ARQ_BAIRROS, index=False)
    print(f"WorldCover 2021: média da cidade {valores.mean():.1f}%")


def escrever_resumo(caminho, anos_novos):
    """Texto em Markdown com o que mudou, usado na descrição do PR automático."""
    def br(valor, fmt):
        return format(valor, fmt).replace(".", ",")

    h = pd.read_csv(ARQ_HISTORICO)
    ultimo, primeiro = h["ano"].max(), h["ano"].min()
    atual = h[h["ano"] == ultimo].set_index("NOME")["vegetacao"]
    linhas = [f"Novos anos do MapBiomas (coleção 10 m): {', '.join(map(str, anos_novos))}.", "",
              f"Média dos bairros em {ultimo}: **{br(atual.mean(), '.1f')}%** de vegetação.", ""]
    if ultimo - 1 in set(h["ano"]):
        antes = h[h["ano"] == ultimo - 1].set_index("NOME")["vegetacao"]
        dif = (atual - antes).sort_values()
        linhas += [f"Maiores quedas de {ultimo - 1} para {ultimo}:", ""]
        linhas += [f"- {n}: {br(v, '+.1f')} p.p." for n, v in dif.head(5).items()]
        linhas += ["", "Maiores aumentos:", ""]
        linhas += [f"- {n}: {br(v, '+.1f')} p.p." for n, v in dif.tail(5)[::-1].items()]
    linhas += ["", f"Série histórica: {primeiro} a {ultimo}."]
    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--worldcover", action="store_true", help="recalcula a cobertura de árvores do WorldCover")
    parser.add_argument("--resumo", help="arquivo onde escrever o resumo das mudanças (Markdown)")
    args = parser.parse_args()

    nomes, geoms = carregar_contornos()
    if args.worldcover:
        atualizar_worldcover(nomes, geoms)
    anos_novos = atualizar_historico(nomes, geoms)

    if args.worldcover or anos_novos:
        # Só regrava quando há dado novo, para o robô não abrir PR sem mudança real
        fontes = json.loads(ARQ_FONTES.read_text(encoding="utf-8")) if ARQ_FONTES.exists() else {}
        hoje = date.today().isoformat()
        if args.worldcover:
            fontes["cobertura_arborea"] = {
                "fonte": "ESA WorldCover 10 m, versão 2021 (v200)",
                "url": WORLDCOVER_URL,
                "classes": WORLDCOVER_ARVORES,
                "ano": 2021,
                "calculado_em": hoje,
            }
        if anos_novos:
            fontes["historico_vegetacao"] = {
                "fonte": "MapBiomas, coleção de 10 m (coleção 4)",
                "url": f"{MAPBIOMAS_BUCKET}/{MAPBIOMAS_PASTA}",
                "classes": MAPBIOMAS_VEGETACAO,
                "anos": sorted(int(a) for a in pd.read_csv(ARQ_HISTORICO)["ano"].unique()),
                "atualizado_em": hoje,
            }
        ARQ_FONTES.write_text(json.dumps(fontes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.resumo and anos_novos:
        escrever_resumo(args.resumo, anos_novos)


if __name__ == "__main__":
    main()
