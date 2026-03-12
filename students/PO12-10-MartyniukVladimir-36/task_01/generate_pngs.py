import os
import urllib.parse
import urllib.request

# Папка с диаграммами
diagrams_dir = "doc/diagrams"
puml_files = [
  "sequence-happy.puml",
  "sequence-error-duplicate.puml",
  "sequence-error-db.puml"
]

for puml_file in puml_files:
  puml_path = os.path.join(diagrams_dir, puml_file)
  png_path = os.path.join(diagrams_dir, puml_file.replace('.puml', '.png'))

  print(f"Обработка {puml_file}...")

  # Читаем содержимое .puml файла
  with open(puml_path, 'r', encoding='utf-8') as f:
    puml_content = f.read()

  # Удаляем @startuml и @enduml для URL
  puml_for_url = puml_content.replace('@startuml', '').replace('@enduml', '').strip()

  # Кодируем для URL
  encoded = urllib.parse.quote(puml_for_url)

  # Формируем URL для получения PNG
  url = f"http://www.plantuml.com/plantuml/png/{encoded}"

  print(f"Загрузка с {url}")

  try:
    # Скачиваем PNG используя urllib (встроенная библиотека, не требует установки)
    urllib.request.urlretrieve(url, png_path)
    print(f"✓ Сохранено: {png_path}")
  except Exception as e:
    print(f"✗ Ошибка загрузки: {e}")

print("Готово!")
