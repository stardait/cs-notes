-- 第 04 章初次安装。先确认这些表名尚未使用，再整份执行。
-- 第 01～05 篇分别用 c4a_～c4e_，基线相同，互不影响。
USE learn;

CREATE TABLE c4a_employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_no VARCHAR(8) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    department VARCHAR(12) NOT NULL,
    grade ENUM('A', 'B', 'C') NOT NULL DEFAULT 'C',
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    hired_on DATE NOT NULL,
    status ENUM('active', 'left') NOT NULL DEFAULT 'active',
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c4a_employees
    (id, employee_no, name, department, grade, salary, hired_on, status, deleted_at, created_at)
VALUES
    (1, 'E001', '林青', '技术部', 'A', 10000.00, '2020-06-01', 'active', NULL, '2026-10-01 09:00:00'),
    (2, 'E002', '周宁', '技术部', 'B',  8000.00, '2022-04-12', 'active', NULL, '2026-10-01 09:00:00'),
    (3, 'E003', '许诚', '技术部', 'B',  6000.00, '2023-01-01', 'active', NULL, '2026-10-01 09:00:00'),
    (4, 'E004', '陈禾', '市场部', 'A',  9000.00, '2021-03-15', 'active', NULL, '2026-10-01 09:00:00'),
    (5, 'E005', '唐雨', '市场部', 'B',  7000.00, '2022-12-31', 'left',   NULL, '2026-10-01 09:00:00'),
    (6, 'E006', '方岚', '行政部', 'B',  5000.00, '2023-01-01', 'left',   NULL, '2026-10-01 09:00:00'),
    (7, 'E007', '罗一', '技术部', 'A', 11000.00, '2021-02-02', 'left',   NULL, '2026-10-01 09:00:00'),
    (8, 'E008', '吴昕', '行政部', 'C',  5000.00, '2022-11-19', 'active', NULL, '2026-10-01 09:00:00'),
    (9, 'E009', '周宁', '市场部', 'C',  5000.00, '2024-01-01', 'active', NULL, '2026-10-01 09:00:00');

CREATE TABLE c4b_employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_no VARCHAR(8) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    department VARCHAR(12) NOT NULL,
    grade ENUM('A', 'B', 'C') NOT NULL DEFAULT 'C',
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    hired_on DATE NOT NULL,
    status ENUM('active', 'left') NOT NULL DEFAULT 'active',
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c4b_employees
    (id, employee_no, name, department, grade, salary, hired_on, status, deleted_at, created_at)
VALUES
    (1, 'E001', '林青', '技术部', 'A', 10000.00, '2020-06-01', 'active', NULL, '2026-10-01 09:00:00'),
    (2, 'E002', '周宁', '技术部', 'B',  8000.00, '2022-04-12', 'active', NULL, '2026-10-01 09:00:00'),
    (3, 'E003', '许诚', '技术部', 'B',  6000.00, '2023-01-01', 'active', NULL, '2026-10-01 09:00:00'),
    (4, 'E004', '陈禾', '市场部', 'A',  9000.00, '2021-03-15', 'active', NULL, '2026-10-01 09:00:00'),
    (5, 'E005', '唐雨', '市场部', 'B',  7000.00, '2022-12-31', 'left',   NULL, '2026-10-01 09:00:00'),
    (6, 'E006', '方岚', '行政部', 'B',  5000.00, '2023-01-01', 'left',   NULL, '2026-10-01 09:00:00'),
    (7, 'E007', '罗一', '技术部', 'A', 11000.00, '2021-02-02', 'left',   NULL, '2026-10-01 09:00:00'),
    (8, 'E008', '吴昕', '行政部', 'C',  5000.00, '2022-11-19', 'active', NULL, '2026-10-01 09:00:00'),
    (9, 'E009', '周宁', '市场部', 'C',  5000.00, '2024-01-01', 'active', NULL, '2026-10-01 09:00:00');

CREATE TABLE c4c_employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_no VARCHAR(8) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    department VARCHAR(12) NOT NULL,
    grade ENUM('A', 'B', 'C') NOT NULL DEFAULT 'C',
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    hired_on DATE NOT NULL,
    status ENUM('active', 'left') NOT NULL DEFAULT 'active',
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c4c_employees
    (id, employee_no, name, department, grade, salary, hired_on, status, deleted_at, created_at)
VALUES
    (1, 'E001', '林青', '技术部', 'A', 10000.00, '2020-06-01', 'active', NULL, '2026-10-01 09:00:00'),
    (2, 'E002', '周宁', '技术部', 'B',  8000.00, '2022-04-12', 'active', NULL, '2026-10-01 09:00:00'),
    (3, 'E003', '许诚', '技术部', 'B',  6000.00, '2023-01-01', 'active', NULL, '2026-10-01 09:00:00'),
    (4, 'E004', '陈禾', '市场部', 'A',  9000.00, '2021-03-15', 'active', NULL, '2026-10-01 09:00:00'),
    (5, 'E005', '唐雨', '市场部', 'B',  7000.00, '2022-12-31', 'left',   NULL, '2026-10-01 09:00:00'),
    (6, 'E006', '方岚', '行政部', 'B',  5000.00, '2023-01-01', 'left',   NULL, '2026-10-01 09:00:00'),
    (7, 'E007', '罗一', '技术部', 'A', 11000.00, '2021-02-02', 'left',   NULL, '2026-10-01 09:00:00'),
    (8, 'E008', '吴昕', '行政部', 'C',  5000.00, '2022-11-19', 'active', NULL, '2026-10-01 09:00:00'),
    (9, 'E009', '周宁', '市场部', 'C',  5000.00, '2024-01-01', 'active', NULL, '2026-10-01 09:00:00');

CREATE TABLE c4d_employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_no VARCHAR(8) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    department VARCHAR(12) NOT NULL,
    grade ENUM('A', 'B', 'C') NOT NULL DEFAULT 'C',
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    hired_on DATE NOT NULL,
    status ENUM('active', 'left') NOT NULL DEFAULT 'active',
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c4d_employees
    (id, employee_no, name, department, grade, salary, hired_on, status, deleted_at, created_at)
VALUES
    (1, 'E001', '林青', '技术部', 'A', 10000.00, '2020-06-01', 'active', NULL, '2026-10-01 09:00:00'),
    (2, 'E002', '周宁', '技术部', 'B',  8000.00, '2022-04-12', 'active', NULL, '2026-10-01 09:00:00'),
    (3, 'E003', '许诚', '技术部', 'B',  6000.00, '2023-01-01', 'active', NULL, '2026-10-01 09:00:00'),
    (4, 'E004', '陈禾', '市场部', 'A',  9000.00, '2021-03-15', 'active', NULL, '2026-10-01 09:00:00'),
    (5, 'E005', '唐雨', '市场部', 'B',  7000.00, '2022-12-31', 'left',   NULL, '2026-10-01 09:00:00'),
    (6, 'E006', '方岚', '行政部', 'B',  5000.00, '2023-01-01', 'left',   NULL, '2026-10-01 09:00:00'),
    (7, 'E007', '罗一', '技术部', 'A', 11000.00, '2021-02-02', 'left',   NULL, '2026-10-01 09:00:00'),
    (8, 'E008', '吴昕', '行政部', 'C',  5000.00, '2022-11-19', 'active', NULL, '2026-10-01 09:00:00'),
    (9, 'E009', '周宁', '市场部', 'C',  5000.00, '2024-01-01', 'active', NULL, '2026-10-01 09:00:00');

CREATE TABLE c4e_employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_no VARCHAR(8) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    department VARCHAR(12) NOT NULL,
    grade ENUM('A', 'B', 'C') NOT NULL DEFAULT 'C',
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    hired_on DATE NOT NULL,
    status ENUM('active', 'left') NOT NULL DEFAULT 'active',
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c4e_employees
    (id, employee_no, name, department, grade, salary, hired_on, status, deleted_at, created_at)
VALUES
    (1, 'E001', '林青', '技术部', 'A', 10000.00, '2020-06-01', 'active', NULL, '2026-10-01 09:00:00'),
    (2, 'E002', '周宁', '技术部', 'B',  8000.00, '2022-04-12', 'active', NULL, '2026-10-01 09:00:00'),
    (3, 'E003', '许诚', '技术部', 'B',  6000.00, '2023-01-01', 'active', NULL, '2026-10-01 09:00:00'),
    (4, 'E004', '陈禾', '市场部', 'A',  9000.00, '2021-03-15', 'active', NULL, '2026-10-01 09:00:00'),
    (5, 'E005', '唐雨', '市场部', 'B',  7000.00, '2022-12-31', 'left',   NULL, '2026-10-01 09:00:00'),
    (6, 'E006', '方岚', '行政部', 'B',  5000.00, '2023-01-01', 'left',   NULL, '2026-10-01 09:00:00'),
    (7, 'E007', '罗一', '技术部', 'A', 11000.00, '2021-02-02', 'left',   NULL, '2026-10-01 09:00:00'),
    (8, 'E008', '吴昕', '行政部', 'C',  5000.00, '2022-11-19', 'active', NULL, '2026-10-01 09:00:00'),
    (9, 'E009', '周宁', '市场部', 'C',  5000.00, '2024-01-01', 'active', NULL, '2026-10-01 09:00:00');

CREATE TABLE c4d_operation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    target_table VARCHAR(64) NOT NULL,
    target_id INT NOT NULL,
    action_name VARCHAR(20) NOT NULL,
    old_salary DECIMAL(10,2) NOT NULL,
    new_salary DECIMAL(10,2) NOT NULL,
    operator_name VARCHAR(100) NOT NULL,
    reason VARCHAR(100) NOT NULL,
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
