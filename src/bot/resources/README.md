### Schema of claim template
[RU] Схема шаблона искового заявления

```json
{
    "type": "object",
    "properties": {
        "theme": {
            "type": "string",
            "required": true
        },
        "story": {
            "type": "object",
            "required": true,
            "properties": {
                "examples": {
                    "type": "array<string>",
                    "required": false
                },
                "actions": {
                    "type": "array<string>",
                    "required": false
                }
            }
        },
        "essence": {
            "type": "object",
            "required": true,
            "properties": {
                "options": {
                    "type": "array<string>",
                    "required": false
                },
                "examples": {
                    "type": "array<string>",
                    "required": false
                }
            }
        },
        "proofs": {
            "type": "object",
            "required": true,
            "properties": {
                "options": {
                    "type": "array<string>",
                    "required": true
                },
                "examples": {
                    "type": "array<string>",
                    "required": false
                }
            }
        },
        "law": {
            "type": "object",
            "required": true,
            "properties": {
                "options": {
                    "type": "array<string>",
                    "required": true
                }
            }
        },
        "claims": {
            "type": "object",
            "required": true,
            "properties": {
                "options": {
                    "type": "array<string>",
                    "required": true
                }
            }
        },
        "additions": {
            "type": "object",
            "required": true,
            "properties": {
                "options": {
                    "type": "array<string>",
                    "required": true
                }
            }
        }
    }
}
```

### Template field description
[RU] Описание полей шаблона. С примером заполненного шаблона можно ознакомиться [тут](./claim_templates/reinstatement.json).
- __theme__ - Уникальное имя искового заявления
- __story__ - Фабула искового заявления
  - _examples_ - Список примеров фабулы для данного типа искового заявления. Поддерживаемые заполнители:
    - end_work_date - дата последнего рабочего дня
  - _actions_ - Список действий, которые нужно совершить пользователю в данном разделе. Поддерживаемые действия:
    - enter_end_date - ввод даты последнего рабочего дня
    - enter_avr_salary - ввод средней месячной заработной платы
- __essence__ - Описание сути нарушения
  - _examples_ - Список примеров сути нарушения для данного типа искового заявления. Поддерживаемые заполнители:
    - start_work_date - дата первого рабочего дня
    - salary - месячная зарплата истца
    - avr_salary - средняя месячная заработная плата истца
    - start_oof_date - дата первого дня вынужденного прогула
    - current_date - текущая дата
    - oof_days - число дней вынужденного прогула
    - oof_profit - вычисленное значение компенсации за время вынужденного прогула
  - _options_ - Список заранее заготовленных опций для выбора
- __proofs__ - Доказательства, предъявляемые истцом
  - _examples_ - Список примеров доказательств для данного типа искового заявления
  - _options_ - Список заранее заготовленных опций для выбора
- __law__ - Нормативные акты, на которые опирается истец в исковом заявлении
  - _options_ - Список заранее заготовленных опций для выбора
- __claims__ - Список требований истца
  - _options_ - Список заранее заготовленных опций для выбора. Поддерживаемые заполнители:
    - defendant - полное имя ответчика (с ИНН, если есть)
    - position - должность истца на рабочем месте
    - start_oof_date - дата первого дня вынужденного прогула
    - current_date - текущая дата
    - oof_profit - вычисленное значение компенсации за время вынужденного прогула
- __additions__ - Приложения для искового заявления
  - _options_ - Список заранее заготовленных опций для выбора

#### Placeholders
[RU] Заполнители
В некоторых значениях полей шаблона поддерживаются т.н. заполнители. Это значения, которые вводит пользователь (или которые вычисляются
на основе введенных им данных). И которые могут быть подставлены в место, указанное в {} фигурных скобках. Например:
```python
# имеем исходную строку в шаблоне "Восстановить истца на работе в {defendant} в должности {position}"
# тут 2 заполнителя - {defendant} и {position}
# при формировании строки для пользователя на место этих заполнителей будут подставленны соответствующие значения
# т.е. пользователь увидит: "Восстановить истца на работе в ООО "Рога и Копыта" в должности инженера"
```