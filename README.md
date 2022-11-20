# Публикация комиксов

Код публикует рандомный комикс и веселый комментарий к нему из [xkcd.com](https://xkcd.com/)

![img](https://imgs.xkcd.com/comics/angular_momentum.jpg)

### Как установить

Для работы скрипта необходимо:
- [зарегистрировать группу](https://vk.com/groups_create) ВКонтакте
- [создать приложение](https://vk.com/editapp?act=create) ВКонтакте (тип - `standalone`) 
- добавить переменные окружения (или файл .env в корне скрипта):

  ACCESS_TOKEN - ключ доступа пользователя. Для его получения необходимо использоваать процедуру [Implicit Flow](https://dev.vk.com/api/access-token/implicit-flow-user) с настройками доступа для приложения `photos, groups, wall и offline`.
  
  GROUP_ID - идентификатор группы, в которую будет оптправлен комикс. Узнать group_id группы можно [здесь](https://regvk.com/id/).


Python3 должен быть уже установлен. 
Затем используйте `pip`  для установки зависимостей:
```bash
pip install -r requirements.txt
```

### Как использовать

Запустить main.py:
```bash
>python main.py
```
Комикс будет загружен в группу.

![image](screenshot/comic.jpg)


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
