-- 手动添加索引优化性能补丁
-- 日期: 2026-02-13

-- 1. 为 RecognitionHistory 表的 user_id 添加索引（加速历史记录查询）
CREATE INDEX ix_recognition_history_user_id ON recognition_history(user_id);

-- 2. 为 FoodTemp 表的 name 添加索引（加速食物搜索）
-- 注意：如果 name 已经有 UNIQUE 约束，通常查询已经很快，但添加普通索引无害
CREATE INDEX ix_food_temp_name ON food_temp(name);

-- 执行完毕后，请重启后端服务确保 SQLAlchemy 元数据同步。
