# import subprocess

# model = "bambucha/saiga-llama3"
# question = "Почему трава зеленая?"

# cmd = [
#     r"C:\Users\tatya\AppData\Local\Programs\Ollama\Ollama.exe",
#     "run",
#     model,
#     question
# ]

# # Запускаем и захватываем вывод
# result = subprocess.run(
#     cmd,
#     capture_output=True
# )

# # Декодируем вручную, чтобы избежать проблем Windows
# stdout = result.stdout.decode("utf-8", errors="ignore")

# print(question)
# print(stdout)

OLLAMA_EXE_CANDIDATES = [
    r"C:\Users\tatya\AppData\Local\Programs\Ollama\Ollama.exe",
    r"C:\Program Files\Ollama\Ollama.exe",
    'ollama'
]

import os

def detect_ollama_executable():
    print("Checking candidates:")
    for path in OLLAMA_EXE_CANDIDATES:
        print("  testing:", path)
        if os.path.exists(path):
            print("FOUND:", path)
            return path
    raise FileNotFoundError("ollama.exe was not found...")

detect_ollama_executable()

