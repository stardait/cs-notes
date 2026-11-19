-- 首次安装。本章独用，已有表时跳过。
USE learn;
CREATE TABLE c7_orders (
    id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    created_at DATETIME NOT NULL,
    status VARCHAR(12) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    INDEX idx_c7_customer_time (customer_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c7_orders (id, customer_id, created_at, status, amount)
WITH digits AS (
    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3
    UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7
    UNION ALL SELECT 8 UNION ALL SELECT 9
), numbers AS (
    SELECT a.n + 10 * b.n + 100 * c.n + 1000 * d.n + 10000 * e.n AS n
    FROM digits AS a
    CROSS JOIN digits AS b
    CROSS JOIN digits AS c
    CROSS JOIN digits AS d
    CROSS JOIN digits AS e
    WHERE e.n < 2
)
SELECT n + 1, MOD(n, 200) + 1,
       DATE_ADD('2026-01-01 00:00:00', INTERVAL n MINUTE),
       IF(MOD(n, 3) = 0, 'pending', 'paid'), 20.00 + MOD(n, 481)
FROM numbers
ORDER BY n;
ANALYZE TABLE c7_orders;
