-- 首次安装。已存在同名表时，先核对表与样本。只补缺表。
USE learn;
CREATE TABLE c5_customers (
    id INT PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    city VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c5_customers (id, name, city) VALUES
    (1, '林青', '杭州'), (2, '周宁', '上海'), (3, '陆遥', '杭州'),
    (4, '陈禾', '北京'), (5, '吴昕', '深圳');

CREATE TABLE c5_products (
    id INT PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    category VARCHAR(30) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL CHECK (current_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c5_products (id, name, category, current_price) VALUES
    (1, '键盘', '配件', 120.00), (2, '鼠标', '配件', 60.00),
    (3, 'USB线', '配件', 30.00), (4, '咖啡豆', '食品', 65.00),
    (5, '茶包', '食品', 25.00), (6, '支架', '配件', 80.00);

CREATE TABLE c5_orders (
    id INT PRIMARY KEY,
    customer_id INT,
    ordered_at DATETIME NOT NULL,
    status ENUM('paid', 'pending', 'cancelled') NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES c5_customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c5_orders (id, customer_id, ordered_at, status) VALUES
    (101, 1,    '2026-10-01 09:00:00', 'paid'),
    (102, 1,    '2026-10-05 10:00:00', 'paid'),
    (103, 2,    '2026-10-05 10:00:00', 'paid'),
    (104, 2,    '2026-10-05 10:00:00', 'pending'),
    (105, 3,    '2026-10-06 10:00:00', 'paid'),
    (106, 4,    '2026-10-07 10:00:00', 'cancelled'),
    (107, NULL, '2026-10-07 12:00:00', 'paid');

CREATE TABLE c5_order_items (
    order_id INT NOT NULL,
    line_no INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, line_no),
    FOREIGN KEY (order_id) REFERENCES c5_orders(id),
    FOREIGN KEY (product_id) REFERENCES c5_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c5_order_items (order_id, line_no, product_id, quantity, unit_price) VALUES
    (101, 1, 1, 1, 100.00), (101, 2, 2, 2, 50.00),
    (102, 1, 2, 1, 55.00), (102, 2, 3, 2, 20.00),
    (103, 1, 4, 2, 60.00), (104, 1, 1, 1, 110.00),
    (105, 1, 1, 1, 105.00), (105, 2, 4, 1, 65.00), (105, 3, 5, 2, 20.00),
    (106, 1, 2, 1, 52.00), (107, 1, 5, 1, 25.00);

CREATE TABLE c5_staff (
    id INT PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES c5_staff(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c5_staff (id, name, manager_id) VALUES (1, '宋言', NULL);
INSERT INTO c5_staff (id, name, manager_id) VALUES (2, '钱晓', 1), (3, '吴青', 1);
