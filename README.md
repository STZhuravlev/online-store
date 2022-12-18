# Проект интернет-магазина
Командный проект
## Разворачивание локального окружения разработки
### Установка необходимого ПО
На хостовую (основную) операционную систему необходимо установить:
- Oracle VM virtual box (возможно понадобится VPN)
- Vagrant (возможно понадобится VPN)
- Pycharm Pro (промокод запросить в службе поддержки студентов)
### Создание виртуальной машини vagrant
1. Запустить окно Oracle VM virtual box
2. В директории проекта запустить консольную команду ```vagrant up```
3. Сразу (не дожидаясь выполнения п.2) переключиться в окно Oracle VM virtual box. Сделать активной создаваемую виртуальную машину (дополнительных окон открывать не надо, просто нажать мышкой один раз)
> первый запуск может длиться 15-20 минут
> во время первого запуска следите, чтобы компьютер не переходил в "сон"
> возможно для первого запуска понадобится VPN
### Управление виртуальной машиной vagrant
* зайти в виртуальную машину
```commandline
vagrant ssh
```
* перезапустить виртуальную машину
```commandline
vagrant reload
```
* выключить виртуальную машину
```commandline
vagrant halt
```
* запустить скрипт установки ПО на виртуальную машину. Скрипт находится в папке `vagrant/provisioning/playbook.yml`. Запускается автоматически при первом выполнении `vargant up`. Эта команда может понадобится только на этапах настройки ВМ.
```commandline
vagrant provision
```
### Работа с проектом внутри локальной машины
* активация виртаульного окружения
```commandline
. ~/venv/bin/activate
```
* перейти в папку проекта
```commandline
cd /vagrant
```
* запустить проект (в папке проекте и внутри активированного виртуального окружения). На хостовой машине проект будет доступен по адресу [http://localhost:8181](http://localhost:8181)
```commandline
python manage.py runserver 0.0.0.0:8181
```
### Настройка интерпретатора для PyCharm Pro
#### Настройка интерпретатора  
В настройках IDE в пункте Project/Python Interpreter добавить интерпретатор Vagrant.  
Путь `/home/vagrant/venv/bin/python` 
#### Запуск сервера разработки  
В *Run/Debug Configurations* добавить Django Server  
host = 0.0.0.0  
port = 8181  
Run Browser http://localhost:8181/  
#### Запуск модульных тестов  
В *Run/Debug Configurations* добавить Django Tests с параметрами по умолчанию
#### Подключение к базе данных  
Через меню *Help/Find Action* найти **Data Sources and Drivers**  
1. Выбрать тип подключения PosgresSQL
2. Настроить SSH: host 127.0.0.1, port 2222, путь до приватного ключа `<папка вашего проекта>\.vagrant\machines\default\virtualbox\private_key`
3. Подключиться к БД: host 127.0.0.1, port 5432,user/password/database - skillbox/skillbox/marketplace
> Возможны проблемы с подключением к БД с примерным сообщением "пользователь не прошёл проверку подлинности по паролю". В этом случае нужно воспользоваться [решением](https://translated.turbopages.org/proxy_u/en-ru.ru.2e0a6176-638b626b-35745e68-74722d776562/https/stackoverflow.com/questions/55038942/fatal-password-authentication-failed-for-user-postgres-postgresql-11-with-pg)
## Запуск проекта в docker-compose
> Запуск проекта производится с хостовой операционной системы в режиме "Продакшн" 

В файле .env расположены "секреты" для доступа к базе данных. В переменной *POSTGRES_PORT* указывает порт проброса из контейнера в хостовую операционную систему.
Запуск осуществляется через nginx и gunicorn. Приложение должно быть доступно на порту 8181.  
**Сборка проекта**
```commandline
docker-compose build
```
**Запуск проекта**
```commandline
docker-compose up -d
```
## Участники проекта
Участник | Часовой пояс
---- | -----
Сергей Ф. | МСК
Сергей М. | МСК 
Стас | МСК
Игорь | МСК
Руслан | МСК 
