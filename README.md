# bicycle
Web chat with crypto encapsulation

## Running
Starts on Python 3.6
Запускать скриптом run.sh
```
./run.sh
```
После запуска модуль запустится в дочернем процессе. Убивать его приходится пока вручную (htop).
TODO: проброс сигнала дочерним процессам
TODO: адекватное управление пакетами (без sys.path)

## Текущее видение
Видимо, вполне удовлетворительным вариантом будет использование TCPServer 
https://docs.python.org/3/library/socketserver.html#socketserver.TCPServer
или его наследников HttpServer.
В репозитории сейчас залит `server.py` - example того, как выглядит простой сервер на сокетах. В реализации TCPServer написано примерно тоже самое.