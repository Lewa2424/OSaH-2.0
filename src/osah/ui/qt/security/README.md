# Qt Security Flow — Встроенный полнофункциональный security контур

## Что изменилось?

Новый Qt UI теперь имеет **полный и обязательный security flow**:

```
Запуск приложения
    ↓
[SecurityFlowController проверяет конфигурацию]
    ├─→ Если НЕ настроено: InitialSetupScreen (установка паролей)
    └─→ Если настроено: LoginScreen (вход с выбором роли)
         ├─→ Успешный вход: AppWindow (authenticated shell)
         └─→ "Забыл пароль": RecoveryAccessScreen (восстановление)
```

## Файлы структуры

```
src/osah/ui/qt/
├── security/
│   ├── __init__.py
│   ├── security_flow_controller.py     ← Главный контроллер
│   └── screens/
│       ├── __init__.py
│       ├── initial_setup_screen.py     ← Первая настройка (чистая установка)
│       ├── login_screen.py             ← Вход с выбором роли
│       └── recovery_access_screen.py   ← Восстановление доступа
├── run_qt_application_secured.py       ← Новая точка входа (заменила старую)
└── run_qt_application.py               ← ДА-ТА использовать! Используйте secured версию
```

## Как запускается

**Основной entry point: `src/osah/main.py`**

```python
from osah.ui.qt.run_qt_application_secured import run_qt_application

# → Это запускает QtApplicationShell с полным security flow
# → НЕ используйте старую run_qt_application() без security!
```

## Security Screens

### InitialSetupScreen
- Показывается при **первом запуске** (когда БД не настроена)
- Пользователь устанавливает два отдельных пароля:
  - Пароль для **INSPECTOR** (полный доступ)
  - Пароль для **MANAGER** (read-only режим)
- После сохранения:
  - Система генерирует recovery-код
  - Система генерирует recovery-файл (хранится отдельно)
  - Переход на LoginScreen

### LoginScreen
- Показывается при **каждом последующем запуске**
- Пользователь выбирает роль (INSPECTOR или MANAGER)
- Вводит пароль для выбранной роли
- Кнопка "Увійти" запускает аутентификацию
- Кнопка "Відновити доступ" → RecoveryAccessScreen

### RecoveryAccessScreen
- Доступна через кнопку на LoginScreen
- Два метода восстановления:
  - **Recovery-код** — для владельца установки
  - **Service-код** — выдается отдельно для поддержки
- После успешного reset:
  - Новые пароли сохраняются
  - Генерируется новый recovery-файл
  - Возврат на LoginScreen

## Разработка / Тестирование

### Если нужно протестировать security flow локально:

```bash
cd "e:\Programming\Python projects\OSaH 2.0"
python main.py
```

Приложение запустится с полным flow:
1. Если БД новая → первый запуск → InitialSetupScreen
2. Если БД уже настроена → LoginScreen

### Если нужно тестировать конкретный экран:

```python
# В скрипте теста:
from osah.ui.qt.security.screens.login_screen import LoginScreen
from osah.application.services.application_context import ApplicationContext

app_context = ApplicationContext(...)
screen = LoginScreen(
    app_context,
    on_authenticated=lambda role: print(f"Authenticated as {role}"),
    on_recovery_requested=lambda: print("Recovery requested")
)
```

## Что удалено?

❌ **Удалён dev shortcut:**
```python
# БЫЛО (в старой run_qt_application.py):
dummy_role = AccessRole.INSPECTOR  # ← Обход security
window = AppWindow(application_context, dummy_role)

# ТЕПЕРЬ:
# Нет никакого dummy_role. Только реальная аутентификация!
```

## Архитектурные принципы

### 1. Security flow управляется SecurityFlowController

```python
controller = SecurityFlowController(
    stacked_widget=self._stacked_widget,
    application_context=application_context,
    on_authenticated=self._on_authenticated  # Callback при успехе
)
```

### 2. Все screens используют application-level services

Не переписываем логику — подключаемся к существующей:
- `load_security_profile()` — проверка конфигурации
- `configure_program_access()` — первая настройка
- `authenticate_program_access()` — вход
- `reset_program_access_with_recovery_code()` — recovery
- `reset_program_access_with_service_code()` — service reset

### 3. Плавный переход между экранами

QStackedWidget управляет видимостью:
- Старый экран скрывается
- Новый экран показывается
- Состояние сохраняется в SecurityFlowController

## Legacy Desktop UI

⚠️ **Важно:**

Старый Tkinter UI в `src/osah/ui/desktop/` содержит работающую реализацию security flow. **Используйте его только как reference для миграции.**

✅ **Все новое пишется в Qt: `src/osah/ui/qt/`**

Читайте: [`src/osah/ui/desktop/LEGACY_NOTICE.md`](./src/osah/ui/desktop/LEGACY_NOTICE.md)

## Статус

✅ **Первый этап архитектурной стабилизации завершён**

- Полный security flow встроен в Qt
- Dev shortcuts удалены
- Legacy UI обозначен как deprecated
- Проект готов к дальнейшему развитию

Читайте полный отчёт: [`STABILIZATION_STEP_REPORT.md`](./STABILIZATION_STEP_REPORT.md)

---

**Автор:** AI Assistant  
**Дата:** 2026-04-22
