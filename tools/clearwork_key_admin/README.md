# ClearWork Key Admin

Mini-програма для генерації та обліку ключів установки ClearWork.

## Запуск

**Портативно (рекомендовано):** подвійний клік по `ClearWorkKeyAdmin.exe` у цій папці.

Поруч мають лежати:
- `keys/private_key.pem`
- `data/` (створюється автоматично)

**Через Python (для розробки):**

```powershell
cd tools/clearwork_key_admin
pip install -r requirements.txt
python main.py
```

## Перезбірка exe

```powershell
cd tools/clearwork_key_admin
powershell -ExecutionPolicy Bypass -File build_key_admin.ps1
```

## Перший запуск

Якщо `keys/private_key.pem` ще немає:

```powershell
python ..\license_demo\generate_keys.py --output-dir keys
```

Потім скопіюйте `keys/public_key.pem` у:

`src/osah/infrastructure/config/setup_key_public_key.pem`

Без цього ClearWork не зможе перевіряти нові ключі.

## Що зберігати у себе

- `keys/private_key.pem` — нікому не передавати
- `data/registry.sqlite3` — локальний облік виданих ключів

## Git

У git потрапляє лише код програми. Не комітьте:

- `keys/private_key.pem`
- `data/`

## Робочий процес

1. Клієнт надсилає **ID установки** з екрана ClearWork.
2. Ви заповнюєте форму в Key Admin.
3. Натискаєте «Згенерувати ключ».
4. Копіюєте рядок `CW-...` і надсилаєте клієнту.
5. Запис автоматично потрапляє в таблицю обліку.

Для перепривязки після втрати `data\` оберіть тип `rebind` і вкажіть попередній запис.
