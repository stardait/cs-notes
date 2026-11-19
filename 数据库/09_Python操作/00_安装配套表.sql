-- SQLite 使用 Python 示例创建独立文件。以下仅用于 MySQL 路线的首次安装。
USE learn;
CREATE TABLE c9_notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL UNIQUE,
    minutes INT NOT NULL CHECK (minutes BETWEEN 1 AND 600)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c9_notes (id, title, minutes) VALUES
    (1, '单表查询', 20), (2, '多表查询', 35);
