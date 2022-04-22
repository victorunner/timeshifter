# Командная утилита (скрипт) `timeshifter`

## Постановка задачи

Предположим, что вам необходимо в исходных данных (из файла, stdin, буфера обмена) сдвинуть все времена
(временные метки вида `9:00`, `12:30` и т.д.) на некоторый временной интервал вперед (или назад).

Например, вам это может потребоваться для изменения расписания конференции (см. пример ниже) при смещении
времени начала конференции, например, на полчаса вперед. Если временных меток достаточно много, то
выполнить коррекцию в ручном режиме крайне затруднительно
(кроме того, риск возникновения ошибок/опечаток при ручном изменении достаточно велик).

schedule.md

```
# Расписание `Awesome Python Conference`

| ВРЕМЯ | ЗАЛ 1    | ЗАЛ 2    |
| ----: | -------- | -------- |
| 9:30  | Открытие | Открытие |
| 9:45  | Доклад А | Доклад С |
| 10:30 | Доклад Б | Доклад Д |
```

Используя скрипт `timeshifter`, приведенную выше задачу можно автоматизировать командой `poetry run timeshifter -i schedule.md -o schedule_modified.md 0:30`.

## Установка

- Установить [poetry](https://python-poetry.org/)
- Склонировать репозиторий в директорию, перейти в эту директорию
- poetry install
- Проверки: `poetry run flake8`, `poetry run pytest`

## Использование

Справка по использованию: `poetry run timeshifter -h`. Далее считаем, что скрипт доступен в системе глобально.

Сдвиг на полчаса вперед:

```
timeshifter -i schedule.md -o schedule_modified.md 0:30
```

Сдвиг на полчаса назад:

```
timeshifter -i schedule.md -o schedule_modified.md -- -0:30
# или
timeshifter -i schedule.md -o schedule_modified.md m0:30
```

Временная метка `24:00`, формально означающая начало следующего дня, перед процедурой сдвига будет трансформирована в `23:59`.

`-i -` = stdin (если опция не указана, то используется по умолчанию)
`-o -` = stdout (если опция не указана, то используется по умолчанию)

Дополнительные варианты использования приведены ниже.

```
echo "See you at 10:00" | timeshifter
timeshifter <<< "See you at 10:00"
```

```
timeshifter <<EOF
See you at 10:00
EOF
```

```
timeshifter -i input.txt
timeshifter < input.txt
timeshifter <<< "See you at 12:00." > output.txt 2>error.txt`
timeshifter <<< "See you at 12:00." &> output.txt
```

## Настройка глобальной работы скрипта

Создайте `runtimeshifter.sh` с содержимым:

```
#!/bin/sh

cd ~/Dev/timeshifter
poetry run timeshifter $@
```

Далее

```
chmod +x runtimeshifter.sh
ln -sf $PWD/runtimeshifter.sh ~/bin/timeshifter
```

Отредактируйте `~/.bashrc`, добавив в конце: `export PATH=$PATH:~/bin`.

# Работа с буфером обмена

Используйте `xsel`.

## Для справки

### Регулярные выражения

- https://realpython.com/regex-python/
- https://realpython.com/regex-python-part-2/
- https://pythex.org/

Branch reset group `(?|...|...)` allows to redefine groups for different alternations. This can be used for numbered groups as well as for named groups.
To use it in python you must install the [regex](https://pypi.org/project/regex/).
General Syntax is `(?|(.)|(.))` where both capturing groups are numbered with `1`, as they occur in different alternations.
The same can be used for named groups for example `(?|(?P<one>1)|(?P<one>one))`.

### argparse

- https://realpython.com/command-line-interfaces-python-argparse/
- https://docs.python.org/3/library/argparse.html
