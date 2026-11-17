# Industrial Empire / MedOil

Постоянная экономическая MMO для Android (Godot 4.x + Go + PostgreSQL + 3D).

## Как любому ИИ продолжить игру

```bash
python tools/work_plan.py validate
python tools/work_plan.py next
python tools/work_plan.py show S0-01
```

1. Прочитай `AGENTS.md` и соответствующий GDD.
2. Возьми первую доступную задачу без открытого PR.
3. Реализуй и открой PR `[ID] Название`.
4. GitHub Actions автоматически сливает обычные PR после минимальных проверок и отмечает задачу `done` после слияния.
5. Новый исполнитель начинает со следующей задачи. Не нужно вручную обновлять ROADMAP.md.

**Ссылки:** `docs/gdd/` (11 глав), `docs/decisions/APPROVED.md`, `docs/architecture/TECH-01.md`, `tasks/tasks.json`, `docs/ROADMAP.md`.

**Важно:** автоматика зависит от разрешений GitHub Actions и настроек защиты ветки. Никакого автоматического развёртывания на VPS.
