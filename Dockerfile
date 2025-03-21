FROM python:3.11-alpine

WORKDIR /app

# Установка зависимостей
RUN apk update && apk add --no-cache gcc musl-dev

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Команда для запуска
CMD ["python", "-m", "src.app"]