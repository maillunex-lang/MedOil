# TECH-01. Техническая архитектура

## Стек
Go modular monolith, PostgreSQL 16+, Godot 4.x Android landscape, 3D isometric, HTTPS JSON API + WebSocket. Монорепозиторий: `server/`, `economy/`, `client/`, `assets/`, `contracts/`, `tools/`, `docs/`. Состав и проверка каркаса — `docs/architecture/MONOREPO-01.md`, манифест `contracts/monorepo/manifest.json`.

## Сервер
Слои: transport → application → domain → repository. Домен: identity, company, world, construction, production, inventory, market, contracts, logistics, population, labor, finance, banking, simulation, events. `net/http`, `pgx`, SQL-миграции, JSON-логи, health/readiness, graceful shutdown. Все критические операции транзакционные.

## Время
360 игровых суток = 604800 реальных секунд. Хранить целые игровые тики, преобразование через рациональные числа; задачи уникальны по типу, сущности и scheduled_tick. Перезапуск без двойного исполнения.

## Данные
Пользователи, компании, города, чанки, участки, здания, оборудование, производственные задания, партии, резервы, биржевые заявки, сделки, контракты, транспорт, домохозяйства, бухгалтерские счета, проводки, кредиты, outbox, audit. Индексы, ограничения, версионирование объектов, миграции без потери данных.

## API
`/api/v1/auth/register`, `/auth/login`, `/auth/refresh`, `/me`, `/companies`, `/companies/me`, `/world/cities`, `/world/chunks/{id}`, `/construction/jobs`, `/enterprises`, `/production/jobs`, `/market/orders`, `/contracts`, `/shipments`, `/finance/summary`, `/loans/applications`. Для команд Idempotency-Key, request_id, стабильные коды ошибок.

## WebSocket
`/api/v1/ws`, потоки company/city/market/chunk/shipment, события с event_id, stream, sequence, schema_version, payload. Проверка прав, replay по курсору, fallback на snapshot. Outbox в той же транзакции, что и изменение состояния.

## Экономика
Эталонные модели и golden-тесты в `economy/`; серверные транзакции в `server/`. Деньги копейки, массы граммы, жидкости мл, энергия Wh, ставки базисные пункты/рациональные. JSON-контракты типов: `contracts/economy/`, см. ECONOMIC-TYPES-01.md. Проверка переполнения, детерминированные округления, двойная запись, учёт эмиссии.

## Android и 3D
Godot: network/state/world/ui, потоковые чанки, кэш, LOD, MultiMesh, safe area, pinch zoom, pan. 20×20 м клетка и 32×32 клетки чанк являются стартовыми параметрами. Ресурсы с asset_id, footprint, visual variants и LOD.

## CI
Минимальные PR-проверки: формат, сборка, схемы, релевантные тесты, миграции, отсутствие секретов. Нагрузочные и длительные тесты на интеграционных этапах. PR и merge SHA подтверждают готовность. Не публиковать APK и не менять VPS без отдельного разрешения.
