# Industrial Empire / MedOil

Постоянная экономическая MMO-стратегия для Android. Рабочий репозиторий `maillunex-lang/MedOil`; название игры: **Industrial Empire**.

## Продолжение работы любым ИИ

1. Прочитать `AGENTS.md`, `docs/decisions/APPROVED.md` и GDD нужной задачи.
2. Выполнить `python tools/work_plan.py validate` и `python tools/work_plan.py next`.
3. Выполнить первую доступную задачу, не пропуская зависимости.
4. Проверить тесты, сделать commit и PR. **Не ставить done в незаслитой ветке.**
5. После слияния PR в main отметить задачу командой `python tools/work_plan.py set ID done --pr NUMBER --sha MERGE_SHA`, закоммитить изменение статуса и `docs/ROADMAP.md`.
6. Если нет возможности подтвердить слияние, оставить задачу `in_progress` и передать ссылку PR следующему исполнителю.

## Содержание
- `docs/gdd/01_*.md` ... `11_*.md`: проект игры.
- `docs/decisions/APPROVED.md`: утверждённые решения.
- `docs/architecture/TECH-01.md`: техническая архитектура.
- `tasks/tasks.json`: единственный источник статусов и зависимостей.
- `docs/ROADMAP.md`: генерируемая дорожная карта.
- `tools/work_plan.py`: проверка, выдача, фиксация статуса.

**VPS не трогать без отдельного разрешения.** Исторические GDD содержат проектные параметры, не реализованный функционал.
