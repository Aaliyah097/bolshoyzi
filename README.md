# Запустить локальные прокси

```bash
privoxy --no-daemon /etc/privoxy/config
```

```python
PROXIES = {
    "http": "http://127.0.0.1:8118",
    "https": "http://127.0.0.1:8118"
}
```

# Тестирование

Запустить отдельный скрипт
```bash
PYTHONPATH=src python3 -c "from src.me.sherlock import *; parse(request('bolshoyzi'));"
```

Мониторинга прокси
```bash
PYTHONPATH=src python3 -m src.proxies.monitor
```

Добавить задачку в очередь
```bash
PYTHONPATH=src pytest src/tests/test_add_task.py -s
```

Дистрибьютор
```bash
PYTHONPATH=src python3 src/distributor/consumer_.py
```

Репортер
```bash
PYTHONPATH=src python3 src/reporter/consumer_.py
```

Запустить бота
```bash
PYTHONPATH=src python3 src/api/bot/main.py
```

# Деплой

Удалить стек
```bash
docker stack rm bolshoyzi
```

Создать файл зависимостей
```bash
pipenv requirements > requirements.txt
```

Собрать образ приложения
```bash
docker build -t bolshoyzi:latest -f Dockerfile .
```

Запустить стек
```bash
docker stack deploy -c swarm-docker-compose.yml --with-registry-auth bolshoyzi
```

# Полезные команды dockerswarm
```bash
# Лог конкретного контейнера
docker logs $(docker ps -qf "name=bolshoyzi_bot.1")
# Запустить докер сварм
docker swarm init
# Посмотреть стеки
docker stack ls
# Посмотреть сервисы стека
docker stack services bolshoyzi
# Инфа по сервису
docker service inspect bolshoyzi_bot
# Список контейнеров сервиса
docker service ps bolshoyzi_bot
# Логи сервиса
docker service logs bolshoyzi_bot
# Обновить и перезапустить сервис
docker service update --force bolshoyzi_bot
# Список волюмов стека
docker volume ls --filter label=com.docker.stack.namespace=bolshoyzi
# Удалить волюмы стека
docker volume rm $(docker volume ls -q --filter label=com.docker.stack.namespace=bolshoyzi)
```
