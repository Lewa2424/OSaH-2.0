# Демонстрация лицензирования ClearWork

Эта папка уже приведена к нормальному рабочему виду, чтобы ты мог просто вырезать её и использовать отдельно от проекта.

## Структура папки

- `generate_keys.py` — создаёт пару ключей.
- `make_license.py` — создаёт и подписывает лицензию.
- `verify_license.py` — проверяет подпись и `device_id`.
- `requirements.txt` — зависимость для этой утилиты.

Подпапки:

- `keys/` — сюда кладутся твои постоянные ключи.
- `requests/` — сюда складываются входные JSON-файлы по клиентам.
- `issued/` — сюда складываются уже выданные лицензии.

## Что хранится постоянно

Постоянно оставляешь у себя:

- `generate_keys.py`
- `make_license.py`
- `verify_license.py`
- `requirements.txt`
- `keys/private_key.pem`
- `keys/public_key.pem`

Важно:

- `private_key.pem` никому не передавать;
- это твой главный секретный ключ;
- `public_key.pem` потом можно встроить в программу.

## Что будет меняться от клиента к клиенту

Для каждого клиента:

- создаёшь или редактируешь JSON в `requests/`
- выпускаешь новую лицензию в `issued/`

То есть в корне папки больше не будет валяться смесь служебных и клиентских файлов.

## Установка зависимости

```powershell
pip install -r requirements.txt
```

## Шаг 1. Создать ключи

По умолчанию ключи создаются в `keys/`:

```powershell
python generate_keys.py
```

Результат:

- `keys/private_key.pem`
- `keys/public_key.pem`

Если ключи уже есть, скрипт не даст случайно их перезаписать.

Если действительно нужно пересоздать ключи:

```powershell
python generate_keys.py --force
```

## Шаг 2. Подготовить запрос клиента

Создаёшь или редактируешь JSON-файл в `requests/`.

Например:

`requests/example_request.json`

```json
{
  "product": "ClearWork",
  "customer": "ТОВ Приклад",
  "device_id": "CW-ABC123-XYZ789",
  "license_type": "single_device",
  "issued_at": "2026-05-20",
  "expires_at": null
}
```

Для нового клиента лучше делать отдельный файл, например:

- `requests/pryklad2.json`
- `requests/energo-zahid.json`

## Шаг 3. Выпустить лицензию

```powershell
python make_license.py --input requests/example_request.json
```

Если `--output` не указан, лицензия автоматически сохраняется в `issued/` с понятным именем.

Например:

- `issued/license-ТОВ-Приклад-CW-ABC123-XYZ789.json`

Если нужен свой путь вывода:

```powershell
python make_license.py ^
  --input requests/example_request.json ^
  --output issued\license-client-001.json
```

## Шаг 4. Проверить лицензию

```powershell
python verify_license.py ^
  --license issued\license-ТОВ-Приклад-CW-ABC123-XYZ789.json ^
  --device-id CW-ABC123-XYZ789
```

Если подпись верная и `device_id` совпадает, проверка проходит успешно.

## Как это будет работать для клиента

1. Клиент устанавливает `ClearWork`.
2. Программа показывает `device_id`.
3. Клиент присылает тебе этот `device_id`.
4. Ты создаёшь JSON-запрос в `requests/`.
5. Выпускаешь лицензию.
6. Получаешь файл в `issued/`.
7. Передаёшь этот файл клиенту.

## Что клиенту передавать

Клиенту передаётся не вся папка, а только готовый файл лицензии из `issued/`.

Например:

- `issued/license-ТОВ-Приклад-CW-ABC123-XYZ789.json`

## Важное ограничение

Это отдельный учебный контур.

Он пока не встроен в:

- установщик;
- экран входа;
- текущую логику хранения лицензии внутри `ClearWork`.

То есть сейчас это уже нормальный отдельный набор для работы с лицензиями, но ещё не интеграция в основную программу.
