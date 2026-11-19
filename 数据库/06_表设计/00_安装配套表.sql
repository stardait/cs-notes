-- 首次安装。用于从旧的平面订单明细建出可核对的结构。
USE learn;
CREATE TABLE c6_legacy_sales (
    order_id INT NOT NULL,
    line_no INT NOT NULL,
    sold_on DATE NOT NULL,
    customer_id INT NOT NULL,
    customer_name VARCHAR(40) NOT NULL,
    city VARCHAR(30) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    product_name VARCHAR(40) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, line_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO c6_legacy_sales
    (order_id, line_no, sold_on, customer_id, customer_name, city, sku, product_name, quantity, unit_price)
VALUES
    (201, 1, '2026-10-01', 1, '林青', '杭州', 'K01', '键盘', 1, 100.00),
    (201, 2, '2026-10-01', 1, '林青', '杭州', 'M01', '鼠标', 2, 50.00),
    (202, 1, '2026-10-02', 1, '林青', '杭州', 'M01', '鼠标', 1, 55.00),
    (203, 1, '2026-10-03', 2, '周宁', '上海', 'K01', '键盘', 1, 105.00);
