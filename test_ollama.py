import subprocess

model = "bambucha/saiga-llama3"
question = "Почему трава зеленая?"

cmd = [
    r"C:\Users\tatya\AppData\Local\Programs\Ollama\Ollama.exe",
    "run",
    model,
    question
]

# Запускаем и захватываем вывод
result = subprocess.run(
    cmd,
    capture_output=True
)

# Декодируем вручную, чтобы избежать проблем Windows
stdout = result.stdout.decode("utf-8", errors="ignore")

print(question)
print(stdout)

