import sys
from faster_whisper import WhisperModel
print("Transcreve .MP3")
print("by Pedro Henrique Sassi")

print("")

model = WhisperModel(
    "turbo",
    device="cpu",
    compute_type="int8"
)

while True:
    if len(sys.argv) < 2:
        arquivo = input("Digite o caminho do arquivo de áudio: ").strip()
        if not arquivo:
            print("Nenhum arquivo informado. Tente novamente.")
            continue
    else:
        arquivo = sys.argv[1]

    segments, info = model.transcribe(
        arquivo,
        language="pt",
        beam_size=1
    )

    saida = arquivo + ".txt"

    with open(saida, "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(segment.text.strip() + "\n")

    print(f"Transcrição salva em: {saida}")

    opcao = input("\n1 - Nova transcrição\n2 - Sair\nEscolha: ").strip()
    if opcao == "2":
        break
    elif opcao == "1":
        sys.argv = [sys.argv[0]]  # limpa argumento para pedir novo arquivo
        continue