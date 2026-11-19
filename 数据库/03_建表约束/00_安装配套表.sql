-- 第 03 章初次安装。先确认这些表名尚未使用，再整份执行。
-- 此脚本仅创建教材表，保留现有数据。已装好时直接进入正文。
USE learn;

CREATE TABLE c3b_type_samples (
    id INT PRIMARY KEY,
    age TINYINT UNSIGNED,
    phone VARCHAR(20),
    country_code CHAR(2),
    bio TEXT,
    exact_amount DECIMAL(10,2),
    float_amount FLOAT,
    double_amount DOUBLE,
    joined_on DATE,
    elapsed TIME,
    local_at DATETIME,
    recorded_at TIMESTAMP,
    state ENUM('pending', 'approved'),
    enabled BOOLEAN
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET @c3_install_time_zone = @@session.time_zone;
SET SESSION time_zone = '+00:00';
INSERT INTO c3b_type_samples
    (id, age, phone, country_code, bio, exact_amount, float_amount, double_amount,
     joined_on, elapsed, local_at, recorded_at, state, enabled)
VALUES
    (1, 18, '01234567890', 'CN', '晚班', 0.10, 0.1, 0.1,
     '2026-10-01', '26:30:00', '2026-10-01 09:00:00', '2026-10-01 09:00:00', 'pending', TRUE),
    (2, 24, NULL, 'NI', NULL, 0.20, 0.2, 0.2,
     '2026-10-02', '00:30:00', '2026-10-02 09:00:00', '2026-10-02 09:00:00', 'approved', FALSE),
    (3, 30, '', 'CN', '', 0.30, 0.3, 0.3,
     '2026-10-03', '01:45:00', '2026-10-03 09:00:00', '2026-10-03 09:00:00', 'pending', NULL);

SET SESSION time_zone = @c3_install_time_zone;

CREATE TABLE c3c_registrations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    registration_no VARCHAR(12) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(100) UNIQUE,
    score DECIMAL(5,2),
    status VARCHAR(12) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_c3c_registration_score CHECK (score BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c3c_registrations
    (id, registration_no, name, email, score, status, created_at)
VALUES
    (1, 'R001', '林青', 'lin@example.test', 86.50, 'approved', '2026-10-01 09:00:00'),
    (2, 'R002', '周宁', NULL, NULL, 'pending', '2026-10-01 09:00:00'),
    (3, 'R003', '陈禾', NULL, 73.00, 'pending', '2026-10-01 09:00:00');

CREATE TABLE c3d_departments (
    id INT PRIMARY KEY,
    dept_name VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c3d_departments (id, dept_name) VALUES
    (10, '技术部'),
    (20, '市场部'),
    (30, '行政部'),
    (40, '支持部'),
    (50, '研究部');

CREATE TABLE c3d_staff_restrict (
    id INT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    dept_id INT NOT NULL,
    CONSTRAINT fk_c3d_restrict FOREIGN KEY (dept_id)
        REFERENCES c3d_departments (id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c3d_staff_restrict (id, name, dept_id)
VALUES (1, '示例员工', 10);

CREATE TABLE c3d_staff_cascade (
    id INT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    dept_id INT NOT NULL,
    CONSTRAINT fk_c3d_cascade FOREIGN KEY (dept_id)
        REFERENCES c3d_departments (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c3d_staff_cascade (id, name, dept_id)
VALUES (1, '示例员工', 20);

CREATE TABLE c3d_staff_nullable (
    id INT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    dept_id INT NULL,
    CONSTRAINT fk_c3d_nullable FOREIGN KEY (dept_id)
        REFERENCES c3d_departments (id)
        ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c3d_staff_nullable (id, name, dept_id)
VALUES (1, '示例员工', 30);

CREATE TABLE c3d_staff_no_action (
    id INT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    dept_id INT NOT NULL,
    CONSTRAINT fk_c3d_no_action FOREIGN KEY (dept_id)
        REFERENCES c3d_departments (id)
        ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO c3d_staff_no_action (id, name, dept_id)
VALUES (1, '示例员工', 40);
