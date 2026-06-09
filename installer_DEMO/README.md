# ClearWork Demo Installer

Окремий інсталятор демонстраційної версії ClearWork з обмеженням **48 годин**.

## Відмінності від звичайного інсталятора

| | `installer/` | `installer_DEMO/` |
|--|--------------|-------------------|
| Файл | `ClearWork-Setup-0.8.3.exe` | `ClearWork-Demo-Setup-0.8.3.exe` |
| Setup key | обов'язковий | не потрібен |
| Демо-засів | опційно (галочка) | завжди |
| Таймер 48h | ні | так |
| Restore з бэкапа | так | заборонено |
| PDF інструкція | так (`ClearWork_швидкий_старт.pdf`) | так |

Після установки на фінальному кроці: галочка **«Відкрити інструкцію»** увімкнена за замовчуванням; **«Запустити ClearWork Demo»** — вимкнена.

## Збірка

```powershell
powershell -ExecutionPolicy Bypass -File installer_DEMO\build_clearwork.ps1
```

Результат: `installer_DEMO\ClearWork-Demo-Setup-0.8.3.exe`

Перед збіркою потрібні: Python 3.12, PyInstaller, Inno Setup 6.

## Маркери після установки

- `ClearWork.demo` — увімкнення демо-засіву
- `ClearWork.demo_timed` — demo-only дистрибуція з таймером

## Роздача клієнтам

Передавайте лише `ClearWork-Demo-Setup-0.8.3.exe`. Попередьте, що після 48 годин потрібна повна версія з ключем установки.
