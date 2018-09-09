# bicycle
Web chat with crypto encapsulation

## Running
Starts on Python 3.x
Запускает локальный тестовый сервер 127.0.0.1:8080
```
python bicycle.py
```

## Текущее видение
Видимо, вполне удовлетворительным вариантом будет использование TCPServer 
https://docs.python.org/3/library/socketserver.html#socketserver.TCPServer
или его наследников HttpServer.
В репозитории сейчас залит `server.py` - example того, как выглядит простой сервер на сокетах. В реализации TCPServer написано примерно тоже самое.