# 🎙️ Transcrever — Transcrição de Áudio com Whisper

Ferramenta de linha de comando para transcrever arquivos de áudio em português usando o modelo **Faster Whisper** localmente, sem depender de APIs externas ou internet.

Criado para resolver uma necessidade real de suporte técnico: **converter gravações de ligações em texto**, facilitando o registro, análise e documentação dos atendimentos realizados.

---

## 💡 Caso de uso

Desenvolvido para equipes de **suporte técnico** que precisam transformar gravações de ligações em texto — permitindo registro mais ágil de chamados, revisão de atendimentos e geração de histórico consultável sem esforço manual.

---



- Transcrição offline com o modelo Whisper Turbo
- Otimizado para português brasileiro
- Suporta múltiplas transcrições em sequência
- Gera arquivo `.txt` automaticamente no mesmo diretório do áudio
- Pode ser distribuído como `.exe` (sem precisar instalar Python)

---

## 📋 Requisitos

- Python 3.9+
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)

Instale as dependências:

```bash
pip install -r requirements.txt
```

Ou manualmente:

```bash
python -m pip install --user faster-whisper ctranslate2 ffmpeg-python
```

---

## 🚀 Como usar

**Pelo terminal:**
```bash
python transcrever.py caminho/para/audio.mp3
```

**Sem argumentos (modo interativo):**
```bash
python transcrever.py
# Digite o caminho do arquivo quando solicitado
```

O arquivo de saída será salvo com o nome `audio.mp3.txt` no mesmo local do áudio.

---

## 📦 Gerar executável (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile transcrever.py
```

O `.exe` será gerado na pasta `dist/`.

---

## 🛠️ Tecnologias

- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) — transcrição eficiente com CTranslate2
- Modelo: `turbo` | Dispositivo: CPU | Quantização: int8
