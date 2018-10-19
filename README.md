# bicycle
Web chat with crypto encapsulation

## Требования
Версия Python: `>=Python3.5`

В модуле `DBManager` импортируется `tinydb`. Установить её можно через `pip`:
```
pip install tinydb
```

## Запуск
```
python bicycle.py
```

Запуск отдельных модулей:
```
python run/web_server_start.py
python run/db_manager_start.py
```

Запуск через скрипт `./run.sh` пока что не актуален и не гарантирует работу.


## Текущее видение
В качестве сервера используется dummy-сервер, написанный "на коленке"
-> TODO: сделать сервер "покурче"

Основная задача (помимо добивания функционала) - процесс генерации ключей и шифрование.
