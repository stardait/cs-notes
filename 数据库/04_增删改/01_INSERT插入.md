# 第 04 章 · INSERT 插入

> 你写的列名决定值应该放到哪一栏。你省略的列，则交给表定义决定。

## 学习目标

- 指定列插一行或多行，预判自增、默认值及空值的结果。
- 在同一个连接取新编号，分辨四类常见写入失败。
- 看懂主键或唯一键冲突时，三种不同的处理方式。

## 准备

这篇使用 `c4a_employees`，初始 9 行。`employee_no` 是业务工号且唯一，`id` 是自增主键。各代码块独立，按顺序读。演示成功的写入在同一个查询标签内用 `ROLLBACK` 收回，预期错误块各自单独执行。

```sql
USE learn;
SELECT COUNT(*) AS starting_rows FROM c4a_employees;
DESCRIBE c4a_employees;
```

## 一、让每个值对上它的列

往名册添一个人，先想哪些栏你手头有值，哪些栏行规已经决定。这条语句提供工号、姓名、部门、工资和入职日期。`VALUES` 里第一个值对应第一个列名，顺着数下去。

```sql
START TRANSACTION;
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('N101', '赵星', '技术部', 6500.00, '2026-10-15');

SELECT LAST_INSERT_ID() AS generated_id;
SELECT employee_no, grade, status, deleted_at, created_at IS NOT NULL AS has_time
FROM c4a_employees WHERE employee_no = 'N101';
ROLLBACK;
```

| employee_no | grade | status | deleted_at | has_time |
|---|---|---|---|---:|
| N101 | C | active | NULL | 1 |

这里的 `LAST_INSERT_ID()` 是当前连接最近一次成功语句生成的第一个自增值。在同一连接紧跟 `INSERT` 查询它，方便知道新行的编号。初次运行通常是 10，重跑可能上升。回滚会收回记录，自增号可能已经消耗。不要用 `MAX(id)` 取自己的新编号，其他连接也可能正在插数据。

可以省略列名，但每个值得严格按整张表的列顺序填写。为展示这种写法，下面完整提供了十个位置，`DEFAULT` 由表定义填值。业务代码推荐写明列名，表将来加列或调整列顺序时，更容易发现和修复问题。

```sql
START TRANSACTION;
INSERT INTO c4a_employees
VALUES (DEFAULT, 'N102', '宋言', '市场部', DEFAULT, 7200.00,
        '2026-10-16', DEFAULT, NULL, DEFAULT);
SELECT employee_no, grade, status FROM c4a_employees WHERE employee_no = 'N102';
ROLLBACK;
```

仍得到默认等级 `C` 和状态 `active`。`DEFAULT` 请求数据库用默认值。`NULL` 是你显式提供的缺失值。对必填列直接给 `NULL` 会失败，即使已有默认值。

## 二、一次插多行，单独指定编号

多行用多个值组，共享同一组列名。下面用每行可不同的等级和一样的默认规则。

```sql
START TRANSACTION;
INSERT INTO c4a_employees (employee_no, name, department, grade, salary, hired_on)
VALUES
    ('N103', '吴青', '行政部', 'B', 7100.00, '2026-10-17'),
    ('N104', '王青', '行政部', DEFAULT, 6900.00, '2026-10-17');
SELECT ROW_COUNT() AS inserted;
SELECT employee_no, grade, salary
FROM c4a_employees WHERE employee_no IN ('N103', 'N104') ORDER BY employee_no;
ROLLBACK;
```

插入 2 行。`N103` 是 `B`、`7100.00`，`N104` 是 `C`、`6900.00`。如果普通插入里的某一行违反唯一约束，InnoDB 会拒绝整条语句，本条语句里的其他行也不会插进去。

迁移或测试时可以显式给自增列一个没被占用的值。显式值足够大时，可能推高之后的自动发号位置。下面的 10000 只用来演示，回滚后行消失，自增计数可能跳到 10001 或更高。

```sql
START TRANSACTION;
INSERT INTO c4a_employees (id, employee_no, name, department, salary, hired_on)
VALUES (10000, 'N105', '林雨', '行政部', 6100.00, '2026-10-17');
SELECT id, employee_no FROM c4a_employees WHERE employee_no = 'N105';
ROLLBACK;
```

返回 `10000, N105`。显式给出的编号仍受主键约束。

## 三、先读懂报错，再动手改

分别选中下列代码块运行。它们都不会写入数据，第一条出错就直接看错误码和列名。

```sql
-- 预期错误 1136
INSERT INTO c4a_employees (employee_no, name) VALUES ('N106');
```

列和值个数不等。先数位置，一般比盯着报错英文找得快。

```sql
-- 预期错误 1364
INSERT INTO c4a_employees (employee_no, department, salary, hired_on)
VALUES ('N106', '技术部', 6500.00, '2026-10-17');
```

遗漏没有默认值的必填列 `name`。若写了列但显式传 `NULL`，通常是 `1048`。

```sql
-- 预期错误 1062
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('E001', '同工号', '技术部', 6500.00, '2026-10-17');
```

`E001` 已经存在，工号唯一约束拦住了写入。新人的姓名不同也过不了。

```sql
-- 预期错误 1054
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES (N106, '宋言', '技术部', 6500.00, '2026-10-17');
```

`N106` 没有单引号，MySQL 会把它当作标识符来找。文本和日期按本章示例写单引号。

```sql
-- 预期错误 1406
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('TOO-LONG-001', '宋言', '技术部', 6500.00, '2026-10-17');
```

`employee_no` 最多 8 字符。本机严格模式下报 `1406`。如果用了 `IGNORE`，过长字符串可能被截断并出现 `1265` 警告。不要拿处理重复值的写法顺手吞掉这类输入问题。

## 四、冲突处理选读

先决定业务希望保留什么。下面用同一个 `E001` 分三次演示，每次回滚，所以原始记录依然是 `id=1`、姓名「林青」、等级 `A`、工资 `10000.00`。

### 跳过冲突

```sql
START TRANSACTION;
INSERT IGNORE INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('E001', '尝试覆盖', '技术部', 11000.00, '2020-06-01');
SHOW WARNINGS;
SELECT id, name, salary FROM c4a_employees WHERE employee_no = 'E001';
ROLLBACK;
```

重复行未插入，`SHOW WARNINGS` 能看到 `1062`，原姓名和原工资仍在。`IGNORE` 也可能把其他输入错误变成警告。每次都查看警告和实际写入结果。

### 更新指定列

```sql
START TRANSACTION;
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('E001', '尝试覆盖', '技术部', 11000.00, '2020-06-01')
ON DUPLICATE KEY UPDATE salary = 11000.00;
SELECT id, name, salary FROM c4a_employees WHERE employee_no = 'E001';
ROLLBACK;
```

新工号走插入，冲突时走更新分支。这里得到 `1, 林青, 11000.00`。只修改分支里指定的 `salary`，表中其他值保留。多个唯一键都可能冲突时，要先确认你能唯一预测命中哪条记录。

### 替换整行

```sql
START TRANSACTION;
REPLACE INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('E001', '新档案', '技术部', 11000.00, '2020-06-01');
SELECT id, name, grade, salary FROM c4a_employees WHERE employee_no = 'E001';
ROLLBACK;
```

`REPLACE` 冲突时按删除旧行再插入新行的语义执行。此处工号一样，`id` 重新分配，显示名为「新档案」，等级重用默认值 `C`。真实表若被外键引用，还可能触发删除约束或级联。

## 小结

普通写入优先列出列名，核对一一对应关系。新行出现后，用工号或新主键确认实际结果。遇见唯一键冲突时，先决定保留现有记录、更新指定字段，还是确实要重建整行。

## 动手练习

### 练习 1 · 最少能填哪些

插入 `N111` 林晓，部门市场部，工资 7500，入职日 2026-10-18，其他列交给默认规则。验证等级与状态。

<details>
<summary>展开参考答案</summary>

```sql
START TRANSACTION;
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('N111', '林晓', '市场部', 7500.00, '2026-10-18');
SELECT employee_no, grade, status FROM c4a_employees WHERE employee_no = 'N111';
ROLLBACK;
```

应看到 `N111, C, active`。

</details>

### 练习 2 · 多行的后半句

一次写入 `N112` 和 `N113`，都在行政部，同一天入职，给两人不同工资。检查影响行数与保存结果。

<details>
<summary>展开参考答案</summary>

```sql
START TRANSACTION;
INSERT INTO c4a_employees (employee_no, name, department, salary, hired_on)
VALUES ('N112', '钱晓', '行政部', 5500.00, '2026-10-18'),
       ('N113', '孙晓', '行政部', 6000.00, '2026-10-18');
SELECT ROW_COUNT() AS inserted;
SELECT employee_no, salary FROM c4a_employees
WHERE employee_no IN ('N112', 'N113') ORDER BY employee_no;
ROLLBACK;
```

影响 2 行，工资依次 5500.00 与 6000.00。

</details>

### 练习 3 · 导入冲突怎么处理

旧的 `E001` 要保持原 `id`、姓名、等级，只调整工资。三种冲突处理选哪种？若确认只改一行现有记录呢？

<details>
<summary>展开参考答案</summary>

要把新增与既有工号的修改放到同条语句时，用 `ON DUPLICATE KEY UPDATE`，只给 `salary` 赋值。若已知只修改既有行，用下一篇的 `UPDATE … WHERE`，可以把目标和改动写得更清楚。

</details>

**下一篇**：[修改现有行](02_UPDATE修改.md)
