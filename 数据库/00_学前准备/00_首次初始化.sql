-- 仅供空环境首次初始化。若 learn.students 已存在，跳过此文件。
-- 在 HeidiSQL 中每条分别执行并检查。CREATE TABLE 失败时不要继续执行 INSERT。
CREATE DATABASE IF NOT EXISTS learn CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE learn;

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    class VARCHAR(20),
    score DECIMAL(5,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO students (id, name, age, class, score) VALUES
    (1, '小明', 18, '一班', 92.50),
    (2, '小红', 17, '一班', 88.00),
    (3, '小刚', 19, '二班', 76.50),
    (4, '小美', 18, '二班', 95.00),
    (5, '小强', 17, '一班', 61.00);
