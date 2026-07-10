import os
import sys
from typing import Optional, Tuple

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Erro: a biblioteca 'faster-whisper' não está instalada.")
    print("Instale com: pip install faster-whisper")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("Erro: a biblioteca 'tqdm' não está instalada.")
    print("Instale com: pip install tqdm")
    sys.exit(1)


MODELO = "turbo"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
IDIOMA = "pt"          # Use None para autodetectar o idioma.
BEAM_SIZE = 5          # Mais preciso que beam_size=1, com custo moderado.
USAR_VAD = True        # Remove trechos sem fala antes da transcrição.
MOSTRAR_SEGMENTOS = True


def limpar_caminho(caminho: str) -> str:
    """Remove espaços e aspas comuns quando o usuário cola o caminho no terminal."""
    return caminho.strip().strip('"').strip("'")


def formatar_tempo(segundos: Optional[float]) -> str:
    if segundos is None:
        segundos = 0

    segundos_int = int(max(segundos, 0))
    horas, resto = divmod(segundos_int, 3600)
    minutos, segundos_int = divmod(resto, 60)

    if horas:
        return f"{horas:02d}:{minutos:02d}:{segundos_int:02d}"
    return f"{minutos:02d}:{segundos_int:02d}"


def obter_arquivo() -> Optional[str]:
    """Lê o arquivo por argumento de linha de comando ou por input interativo."""
    if len(sys.argv) >= 2:
        arquivo = limpar_caminho(sys.argv[1])
        sys.argv = [sys.argv[0]]  # Consome o argumento para não repetir o mesmo arquivo no loop.
        return arquivo

    arquivo = limpar_caminho(input("Digite o caminho do arquivo de áudio: "))
    if not arquivo:
        print("Nenhum arquivo informado. Tente novamente.")
        return None

    return arquivo


def validar_arquivo(arquivo: str) -> bool:
    if not os.path.exists(arquivo):
        print(f"Arquivo não encontrado: {arquivo}")
        return False

    if not os.path.isfile(arquivo):
        print(f"O caminho informado não é um arquivo: {arquivo}")
        return False

    return True


def caminho_saida(arquivo: str) -> str:
    base, _extensao = os.path.splitext(arquivo)
    return base + ".txt"


def atualizar_barra(pbar: tqdm, posicao_atual: float, posicao_anterior: float, duracao: float) -> float:
    """Atualiza a barra do tqdm usando segundos de áudio processados."""
    if duracao <= 0:
        pbar.update(1)
        return posicao_anterior

    posicao_atual = min(max(posicao_atual, 0), duracao)
    incremento = posicao_atual - posicao_anterior

    if incremento > 0:
        pbar.update(incremento)
        return posicao_atual

    return posicao_anterior


def transcrever_arquivo(model: WhisperModel, arquivo: str) -> Tuple[str, int]:
    saida = caminho_saida(arquivo)

    print(f"\nTranscrevendo: {arquivo}")
    print(f"Saída: {saida}")

    segments, info = model.transcribe(
        arquivo,
        language=IDIOMA,
        beam_size=BEAM_SIZE,
        vad_filter=USAR_VAD,
    )

    duracao = float(getattr(info, "duration", 0) or 0)
    idioma_detectado = getattr(info, "language", None)
    probabilidade_idioma = getattr(info, "language_probability", None)

    if duracao:
        print(f"Duração: {formatar_tempo(duracao)}")

    if idioma_detectado:
        if probabilidade_idioma is not None:
            print(f"Idioma: {idioma_detectado} ({probabilidade_idioma:.1%} de confiança)")
        else:
            print(f"Idioma: {idioma_detectado}")

    print("\nIniciando transcrição...")

    total_segmentos = 0
    progresso_anterior = 0.0

    total_barra = duracao if duracao > 0 else None
    unidade_barra = "s" if duracao > 0 else "segmento"

    with open(saida, "w", encoding="utf-8") as f, tqdm(
        total=total_barra,
        unit=unidade_barra,
        desc="Progresso",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}| {percentage:3.0f}% [{elapsed}<{remaining}]" if duracao > 0 else None,
    ) as pbar:
        for segment in segments:
            texto = segment.text.strip()
            fim_segmento = float(getattr(segment, "end", 0) or 0)

            progresso_anterior = atualizar_barra(
                pbar=pbar,
                posicao_atual=fim_segmento,
                posicao_anterior=progresso_anterior,
                duracao=duracao,
            )

            if texto:
                total_segmentos += 1
                f.write(texto + "\n")

        if duracao > 0 and progresso_anterior < duracao:
            pbar.update(duracao - progresso_anterior)

    return saida, total_segmentos


def perguntar_proxima_acao() -> str:
    while True:
        opcao = input("\n1 - Nova transcrição\n2 - Sair\nEscolha: ").strip()

        if opcao in {"1", "2"}:
            return opcao

        print("Opção inválida. Digite 1 para nova transcrição ou 2 para sair.")


def main() -> None:
    print("Transcreve .MP3")
    print("by Pedro Henrique Sassi")
    print()

    print("Carregando modelo... isso acontece apenas uma vez.")
    model = WhisperModel(
        MODELO,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
    )
    print("Modelo carregado.\n")

    while True:
        arquivo = obter_arquivo()
        if not arquivo:
            continue

        if not validar_arquivo(arquivo):
            continue

        try:
            saida, total_segmentos = transcrever_arquivo(model, arquivo)
            print(f"Transcrição salva em: {saida}")
            print(f"Segmentos gravados: {total_segmentos}")
        except Exception as erro:
            print(f"\nErro ao transcrever '{arquivo}': {erro}")
            print("Verifique se o arquivo é um áudio válido e tente novamente.")
            continue

        if perguntar_proxima_acao() == "2":
            break

    print("Encerrado.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
