-- 首次安装。事务练习的 DML 都在这些表上完成。
USE learn;
CREATE TABLE c8_accounts (
    id INT PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    balance DECIMAL(10,2) NOT NULL CHECK (balance >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c8_accounts (id, name, balance) VALUES
    (1, '林青', 1000.00), (2, '周宁', 500.00), (3, '陆遥', 200.00);
