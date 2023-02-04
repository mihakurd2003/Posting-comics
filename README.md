# Публикация комиксов

Публикация комиксов во Вконтакте

### Как установить

- Скачайте код и поместите в виртуальное окружение
```
python3 -m venv <название окружения>
```
```
<название окружения>\Scripts\activate.bat
```
```
git clone https://github.com/mihakurd2003/Posting-comics.git
```

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Перед запуском создайте файл .env и в нём пропишите:

- VK_TOKEN=<access token созданного вами приложения во Вконтакте>
- VK_GROUP_ID=<id созданной вами группы во Вконтакте>
### Как пользоваться файлом main.py
- В терминале набирайте команду:
```
python3 main.py
```
- Получает случайный комикс с сайта [xkcd.com](https://xkcd.com/) и публикует его в группу во Вконтакте