# bicycle
Web chat with crypto encapsulation

## Running
Запускать скриптом **run.sh**
```
./run.sh
```
либо напрямую через Python:
```
python3.6 bicycle.py
```

Запуск отдельных модулей:
```
python3.6 run/web_server_start.py
python3.6 run/db_manager_start.py
```



Возможен запуск из виртуального окружения. Для этого не обходимо передать ключ **-e**:
```
./run.sh -e
```

## Текущее видение
Видимо, вполне удовлетворительным вариантом будет использование TCPServer 
https://docs.python.org/3/library/socketserver.html#socketserver.TCPServer
или его наследников HttpServer.
В репозитории сейчас залит `server.py` - example того, как выглядит простой сервер на сокетах. В реализации TCPServer написано примерно тоже самое.