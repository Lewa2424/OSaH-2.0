# ClearWork — установка в Windows

Версія поставки: **1.1.3**

## Що встановлюється

`ClearWork-Setup-1.1.3.exe` встановлює ClearWork локально для поточного користувача Windows.

- Папка програми: `%LOCALAPPDATA%\Programs\ClearWork`
- Ярлик у меню Пуск: `ClearWork`
- Ярлик інструкції: `Інструкція ClearWork` → `ClearWork_швидкий_старт.pdf`
- Опційно: ярлик на стільниці

Python окремо встановлювати не потрібно.

## Кроки установки

1. Запустіть `ClearWork-Setup-1.1.3.exe`.
2. Якщо Windows SmartScreen попереджає:
   - `Докладніше`
   - `Все одно запустити`
3. Завершіть майстер установки.
4. На останньому кроці:
   - увімкніть **«Відкрити інструкцію»** (рекомендовано перед першим запуском);
   - **«Запустити ClearWork»** — за бажанням (для робочої версії спочатку потрібен ключ).
5. Для робочої версії: скопіюйте ID установки, отримайте ключ `CW-...`, активуйте програму.

Повна інструкція: `ClearWork_користувач.md` у папці програми.

## SmartScreen

ClearWork збирається без платного code signing. Для офіційної поставки:

- `Докладніше` → `Все одно запустити`

## Перший запуск (робоча версія)

1. Екран активації — вставте ключ установки.
2. Задайте паролі інспектора та керівника.
3. Збережіть файл recovery окремо від папки програми.

Програма автоматично створює робочі каталоги `data\` та `logs\`.

## Де зберігаються дані

- `%LOCALAPPDATA%\Programs\ClearWork\data\` — база
- `%LOCALAPPDATA%\Programs\ClearWork\data\backups\` — резервні копії
- `%LOCALAPPDATA%\Programs\ClearWork\data\recovery\` — відновлення доступу
- `%LOCALAPPDATA%\Programs\ClearWork\logs\` — журнал

## Видалення

1. Параметри Windows → Програми → ClearWork → Видалити  
   або `%LOCALAPPDATA%\Programs\ClearWork\unins000.exe`

За замовчуванням папки `data\` та `logs\` залишаються. Не видаляйте `data\` без резервної копії — там ID установки та база.

## Якщо програма не запускається

1. Переконайтеся, що установка завершилась без помилок.
2. Запустіть `%LOCALAPPDATA%\Programs\ClearWork\ClearWork.exe` напряму.
3. Перевірте `logs\osah.log`.
4. Зверніться: alexeyovch26@gmail.com, +380954553545

## Збірка (для розробника)

- `powershell -ExecutionPolicy Bypass -File installer\build_clearwork.ps1`
- PyInstaller + Inno Setup 6
- PDF інструкції генерується скриптом `installer\generate_quick_start_pdf.py`
