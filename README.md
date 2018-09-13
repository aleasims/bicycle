# bicycle
Web chat with crypto encapsulation

## Running
Запускать скриптом **run.sh** (иначе будут проблемы с зависимостями и переменными окружения)
```
./run.sh
```

(!) Возможен запуск из виртуального окружения. Для этого не обходимо передать ключ **-e**:
```
./run.sh -e
```

## Текущее видение
Видимо, вполне удовлетворительным вариантом будет использование TCPServer 
https://docs.python.org/3/library/socketserver.html#socketserver.TCPServer
или его наследников HttpServer.
В репозитории сейчас залит `server.py` - example того, как выглядит простой сервер на сокетах. В реализации TCPServer написано примерно тоже самое.