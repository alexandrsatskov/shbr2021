## Реализация вступительного задания в yandex backend school 2к21.
Задание: [техническое задание](https://github.com/twinkleToes2001/yandex_backend/docs/assignment.pdf)  
FAQ по заданию: [FAQ](https://github.com/twinkleToes2001/yandex_backend/docs/faq.pdf)

## Приятнейшего вечерочка проверяющему мой вариант реализации вступительного задания в школу backend разработки от Yandex. ##

### Предисловие: ### 
Я начинающий разработчик, и в процессе создания данного приложения я столкнулся со множеством проблем различного характера, начиная мыслями что у меня ничего не получится и заканчивая первым деплоем, но все это не помешало мне в итоге оказаться здесь, финишной черты. 

Как минимум, хочу сказать спасибо, за предоставленную возможность попробовать свои силы и сделать глобальное приложение в контексте своих знаний и умений. 
Безусловно хотелось бы попасть в школу, но учитывая [статью с крепкой реализацией прошлогоднего задания](https://habr.com/ru/company/yandex/blog/499534/), полагаю, шансов у меня маловато)

В статье ней я встретил множетво незнакомых мне слов, технологий, инстументов. Увидев, как должен выглядеть проект, я, было уже опустил руки. Но после - осознал, пусть даже мое решение будет ледышкой на фоне [айсберга](https://habr.com/ru/company/yandex/blog/499534/), я понял, что любой опыт это опыт, в конце концов это шанс получить фидбек от профи и улучшить результат в следующем году.

### _Еще раз спасибо, и удачи тебе, человек перед экраном!_ ###

PS. Не сделал тесты, но все остальное должно работать  ¯\\_(ツ)\_/¯
<br /><br /><br />

# Документирование: #

## 1. Пакеты: ##

* Обновление пакетов:<br />
`sudo apt-get update`

* Необходимые пакеты:<br />
`sudo apt install git python3-pip python3-venv nginx`
* Устанавливаем последнюю версию PostgreSQL:<br />
`sudo apt-get -y install postgresql`

* Подтягиваем проект с github:<br />
`git clone https://github.com/twinkleToes2001/yandex_backend.git`

* Создание и активация виртуальной среды:<br />
`python3 -m venv venv`<br />
`source venv/bin/activate`

* Установка python пакетов:<br />
`pip3 install -r requirements.txt`<br />
`pip3 install psycopg2-binary gunicorn`

## 2. База данных: ##
* В файле config.py находятся переменные для подключения к БД, их нужно будет править под себя, при необходимости.<br />
```
DBMS = 'postgresql'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'
DATABASE_NAME = 'postgres'
DATABASE_USERNAME = 'dev'
DATABASE_PASSWORD = 'root'
```

* Создаем нового юзера для БД (для моего решения создается dev:root)<br />
`sudo -u postgres psql`<br />
`CREATE USER dev with PASSWORD 'root';`<br />
`GRANT ALL PRIVILEGES ON DATABASE postgres to dev;`<br />


## 3. Автозапуск после перезагрузки: ##
* Файл wsgi.service содержит необходимое описание для его использования системой инициализации systemd, все что нужно сделать:
1) Заменить \<user\> на Вашего юзера:
```
[Unit]
Description=YandexBackend_rest-api
After=network.target

[Service]
User=\<user\>
Group=www-data
WorkingDirectory=/home/\<user\>/yandex_backend
Environment="PATH=/home/\<user\>/yandex_backend/venv/bin"
ExecStart=/home/\<user\>/yandex_backend/venv/bin/gunicorn -w 4 -b unix:yandex_backend.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

2) Скопировать файл в /etc/systemd/system/ <br />
`sudo cp -i /home/entrant/yandex_backend/wsgi.service`

* Даем право на автозапуск:<br />
`sudo systemctl enable wsgi`
* Стартуем процесс<br />
`sudo systemctl start wsgi`

## 4. NGINX ##
`sudo ufw allow 'Nginx Full'`

* Создаем файл конфигурации в Nginx's sites-available директории<br />
`sudo nano /etc/nginx/sites-available/yandex_backend`

```
server {
    listen 80;
    server_name 178.154.205.166;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/entract/yandex_backend/yandex_backend.sock;
    }
}
```

* Линкуем созданный файл в sites-enabled директорию<br />
`sudo ln -s /etc/nginx/sites-available/yandex_backend /etc/nginx/sites-enabled`

* Перезапускаем Nginx
`sudo systemctl restart nginx`

# **Насладждаемся** # 
:woozy_face:
