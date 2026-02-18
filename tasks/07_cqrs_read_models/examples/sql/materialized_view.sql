-- =====================================================
-- Materialized View для Request Service
-- ПСО «Юго-Запад»
-- =====================================================

-- Создание Materialized View
CREATE MATERIALIZED VIEW request_view AS
SELECT 
    -- Основные поля заявки
    r.request_id,
    r.status,
    
    -- Данные координатора (денормализовано)
    r.coordinator_id,
    c.name AS coordinator_name,
    c.phone AS coordinator_phone,
    
    -- Данные зоны (денормализовано)
    z.name AS zone_name,
    -- Вычисление площади зоны в км²
    ABS((z.lat_max - z.lat_min) * (z.lon_max - z.lon_min)) * 12365.0 AS zone_area_km2,
    
    -- Данные группы (денормализовано)
    r.assigned_group_id,
    v_leader.name AS group_leader_name,
    COUNT(gm.volunteer_id) AS group_members_count,
    
    -- Временные метки
    r.created_at,
    r.activated_at,
    r.completed_at,
    
    -- Вычисление длительности операции (в минутах)
    CASE 
        WHEN r.activated_at IS NOT NULL AND r.completed_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (r.completed_at - r.activated_at)) / 60
        ELSE NULL
    END AS duration_minutes

FROM requests r

-- JOIN для coordinator
LEFT JOIN coordinators c ON r.coordinator_id = c.coordinator_id

-- JOIN для zone
LEFT JOIN zones z ON r.request_id = z.request_id_fk

-- JOIN для group
LEFT JOIN groups g ON r.assigned_group_id = g.group_id

-- JOIN для group leader
LEFT JOIN volunteers v_leader ON g.leader_id = v_leader.volunteer_id

-- JOIN для подсчёта участников группы
LEFT JOIN group_members gm ON g.group_id = gm.group_id

GROUP BY 
    r.request_id,
    r.status,
    r.coordinator_id,
    c.name,
    c.phone,
    z.name,
    z.lat_min, z.lat_max, z.lon_min, z.lon_max,
    r.assigned_group_id,
    v_leader.name,
    r.created_at,
    r.activated_at,
    r.completed_at;

-- =====================================================
-- Индексы для быстрого поиска
-- =====================================================

-- Уникальный индекс по request_id
CREATE UNIQUE INDEX idx_request_view_id 
ON request_view (request_id);

-- Индекс по статусу (для find_active_requests)
CREATE INDEX idx_request_view_status 
ON request_view (status);

-- Индекс по coordinator_id (для find_by_coordinator)
CREATE INDEX idx_request_view_coordinator 
ON request_view (coordinator_id);

-- Индекс по zone_name (для find_by_zone)
CREATE INDEX idx_request_view_zone 
ON request_view (zone_name);

-- Индекс по completed_at (для find_completed_in_last_days)
CREATE INDEX idx_request_view_completed_at 
ON request_view (completed_at) 
WHERE status = 'COMPLETED';

-- =====================================================
-- Обновление Materialized View
-- =====================================================

-- Ручное обновление (в cron или после изменений)
REFRESH MATERIALIZED VIEW request_view;

-- Concurrently (без блокировки чтения)
REFRESH MATERIALIZED VIEW CONCURRENTLY request_view;

-- =====================================================
-- Автоматическое обновление через триггеры
-- =====================================================

-- Функция для обновления view
CREATE OR REPLACE FUNCTION refresh_request_view()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновление CONCURRENTLY (требует UNIQUE INDEX)
    REFRESH MATERIALIZED VIEW CONCURRENTLY request_view;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Триггер на таблице requests
CREATE TRIGGER trg_refresh_request_view_on_requests
AFTER INSERT OR UPDATE OR DELETE ON requests
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_request_view();

-- Триггер на таблице groups (если меняется состав группы)
CREATE TRIGGER trg_refresh_request_view_on_groups
AFTER INSERT OR UPDATE OR DELETE ON groups
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_request_view();

-- =====================================================
-- Примеры запросов
-- =====================================================

-- Получить заявку по ID (моментально, без JOINов)
SELECT * FROM request_view WHERE request_id = 'REQ-2024-0001';

-- Получить все активные заявки
SELECT * FROM request_view WHERE status = 'ACTIVE';

-- Получить заявки координатора
SELECT * FROM request_view WHERE coordinator_id = 'COORD-1';

-- Получить завершённые заявки за последние 7 дней
SELECT * FROM request_view 
WHERE status = 'COMPLETED' 
  AND completed_at >= NOW() - INTERVAL '7 days'
ORDER BY completed_at DESC;

-- Статистика по зонам
SELECT 
    zone_name,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
    AVG(duration_minutes) AS avg_duration_minutes
FROM request_view
GROUP BY zone_name;

-- =====================================================
-- Преимущества Materialized View
-- =====================================================

-- ✅ Быстрые SELECT (без JOINов)
-- ✅ Предвычисленные агрегаты (COUNT, AVG)
-- ✅ Индексы на денормализованных полях
-- ✅ Автообновление через триггеры

-- ❌ Необходимость REFRESH (можно автоматизировать)
-- ❌ Дублирование данных (но для Read Model это OK)
