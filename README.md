# goit-cs-hw-06

Простий вебзастосунок без вебфреймворків:

- HTTP-сервер на порту `3000`;
- UDP-сервер для повідомлень на порту `5000`;
- збереження повідомлень у MongoDB;
- запуск HTTP- і UDP-серверів у різних процесах.

## Запуск через Docker Compose

Створіть файл налаштувань:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Запустіть застосунок і MongoDB:

```bash
docker compose up --build
```

Для Docker Compose залиште в `.env` такі значення:

```env
SOCKET_HOST_CLIENT=localhost
MONGO_URI=mongodb://mongo:27017
```

HTTP- і UDP-сервери працюють в одному контейнері `app`, тому UDP-повідомлення
надсилаються на `localhost`. MongoDB працює в окремому контейнері та доступна
застосунку через ім'я сервісу `mongo`.

Відкрийте в браузері <http://localhost:3000>.

Форма доступна за адресою <http://localhost:3000/message.html>. Після
надсилання повідомлення воно зберігається в базі `messages_db`, колекції
`messages`.

Перегляд збережених повідомлень:

```bash
docker compose exec mongo mongosh messages_db --eval "db.messages.find().pretty()"
```

Зупинка контейнерів:

```bash
docker compose down
```

Дані MongoDB зберігаються у named volume `mongo_data`, тому не видаляються
після звичайного `docker compose down`.

## Локальний запуск

Для локального запуску потрібні Python 3.13, `uv` і доступна MongoDB.
Синхронізуйте залежності та запустіть застосунок:

```bash
uv sync
uv run main.py
```

Для локальної MongoDB у `.env` використовуйте:

```env
MONGO_URI=mongodb://localhost:27017
SOCKET_HOST_CLIENT=localhost
```