### claimant bot

[EN] This repository contains the source code of [claimant_bot](https://t.me/claimant_bot) telegram bot.
This bot helps people to compose the claim into the court without help from the lawyer side.

[RU] Данный репозиторий содержит исходный код телеграмм бота [claimant_bot](https://t.me/claimant_bot).
Этот бот помогает людям составлять различные исковые заявления в суд не прибегая к помощи профессионального юриста.

#### How to start bot?
1. Firstly, you need to build claimant-bot docker image with command:
```shell
cd ./src/bot & docker build . -t claimant-bot:latest
```
Also, there is a necessary to build clear-db-daemon docker image with command:
```shell
cd ./src/clear_db_daemon & docker build . -t clear-db-daemon:latest
```
2. You need to compose .env file with main bot settings and save it into ./src/bot directory:
```dotenv
API_TOKEN= # The telegram bot token. For testing you can generate a new one with @BotFather bot
ENCRYPT_KEY= # The key for encrypting user data in DB
ADMIN_IDS= # Telegram IDs of admins

MONGO_INITDB_ROOT_USERNAME= # MongoDB root user name
MONGO_INITDB_ROOT_PASSWORD= # MongoDB root user password
MONGO_INITDB_USERNAME= # MongoDB client user name
MONGO_INITDB_PASSWORD= # MongoDB client user password
MONGO_INITDB_DATABASE= # MongoDB database name
MONGO_HOST= # MongoDB host. In case of run with docker-compose it should be 'bot-db'. Otherwhise - 'localhost'.
MONGO_PORT= # MongoDB port. By default - 27017
```
3. When you achieve a correct .env file, you can run bot with docker-compose command from ./src/bot directory:
`docker-compose up -d`

#### About claim templates
[EN]
The main part of claimant-bot is a claim templates. The claim template is a decomposition of claim with a specific theme,
which was built by profession lawyers. It contains predefined options for choosing, examples of life situations and 
describes what action should user do for composing claim properly. You can find the claim template JSON-schema description 
in this [readme](./src/bot/resources/README.md).

[RU] Основной элемент claimant-bot это шаблоны исковых заявлений. Шаблон искового заявления - это декомпозиция
конкретного искового заявления, которая составляется профессиональными юристами. Шаблон содержит заготовленные ответы,
примеры ситуаций, а так же описывает какие действия должен совершить пользователь для правильного составления заявления.
Вы можете найти описание JSON-схемы шаблонов в этой [документации](./src/bot/resources/README.md).