# 第 04 章 · UPDATE 修改

> `WHERE` 决定哪些行能进来，`SET` 决定每一行该变成什么样。

## 学习目标

- 先查目标再更新，写出单列、多列和按原值计算的更新。
- 用 `CASE WHEN` 把不同等级映射到不同新值。
- 读懂匹配条数、变更条数，以及 `ORDER BY` 与 `LIMIT` 改的是哪几行。

## 准备

`c4b_employees` 初始有 9 行。练习统一从同一基线出发。每个带事务的代码块整段执行，它会在结果出现后收回演示写入。单独练习时，也可以先执行到复查，再继续执行最后一条 `ROLLBACK`。

```sql
USE learn;
SELECT id, name, department, grade, salary, status
FROM c4b_employees ORDER BY id;
```

先认三位仍在职的技术部员工。`id=1, 2, 3`，工资依次是 10000、8000、6000。部门里还有 `id=7`，但已经离职。更新题只写部门时，它也会被选中。

## 一、同一条件查一遍、写一遍

把林青的工资改到 10500。你可以把 `WHERE id = 1` 想成先从档案柜抽出编号 1，再改那份档案里的工资栏。

```sql
START TRANSACTION;
SELECT id, name, salary FROM c4b_employees WHERE id = 1;
UPDATE c4b_employees
SET salary = 10500.00
WHERE id = 1;
SELECT ROW_COUNT() AS changed_rows;
SELECT id, salary FROM c4b_employees WHERE id = 1;
ROLLBACK;
```

应看到原工资 10000、变更 1 行，新工资 10500。在 `UPDATE` 之后紧跟 `SELECT ROW_COUNT()`，中间插入别的查询就会拿到上一条新语句的结果。默认连接通常报告实际变更行数，开启 `CLIENT_FOUND_ROWS` 的客户端可报告匹配行数。下面故意把工资设成原值，借此看清为什么「改了零行」也可能已经找到了人。

```sql
START TRANSACTION;
SELECT id, salary FROM c4b_employees WHERE id = 1;
UPDATE c4b_employees SET salary = 10000.00 WHERE id = 1;
SELECT ROW_COUNT() AS changed_or_matched;
ROLLBACK;
```

第一条查出 1 行。默认连接下变更 0 行，配置为匹配行数的连接返回 1。SQL 执行成功后，仍要对照目标编号与实际列值。

## 二、同时改多列，或用各行原值计算

同一个员工转到市场部、职级变为 B。多个赋值用逗号分开。

```sql
START TRANSACTION;
SELECT id, department, grade FROM c4b_employees WHERE id = 1;
UPDATE c4b_employees
SET department = '市场部',
    grade = 'B'
WHERE id = 1;
SELECT ROW_COUNT() AS changed_rows;
SELECT id, department, grade FROM c4b_employees WHERE id = 1;
ROLLBACK;
```

现在改成行政部在职人员加薪 10%。右边 `salary * 1.10` 读取的是各自的工资。只有 `id=8` 符合，已离职的 `id=6` 保持 5000。

```sql
START TRANSACTION;
SELECT id, salary FROM c4b_employees WHERE department = '行政部' AND status = 'active';
UPDATE c4b_employees SET salary = salary * 1.10
WHERE department = '行政部' AND status = 'active';
SELECT ROW_COUNT() AS changed_rows;
SELECT id, status, salary FROM c4b_employees WHERE id IN (6, 8) ORDER BY id;
ROLLBACK;
```

结果中 6 还是 `5000.00`，8 变成 `5500.00`。比例型写入执行两遍会计算两次。实际工作时，断线后先查当前状态和已提交记录，再决定是否重试。

## 三、同一批里，不同等级用不同规则

先选在职技术部。A 加 10%，B 加 5%，其余维持原工资。`CASE` 像一张按等级查加薪比例的表。`WHERE` 跟在 `END` 后，限制可以进入这套规则的行。

```sql
START TRANSACTION;
SELECT id, grade, salary FROM c4b_employees
WHERE department = '技术部' AND status = 'active' ORDER BY id;

UPDATE c4b_employees
SET salary = CASE grade
    WHEN 'A' THEN salary * 1.10
    WHEN 'B' THEN salary * 1.05
    ELSE salary
END
WHERE department = '技术部' AND status = 'active';

SELECT ROW_COUNT() AS changed_rows;
SELECT id, salary FROM c4b_employees WHERE id IN (1, 2, 3, 7) ORDER BY id;
ROLLBACK;
```

| id | 修改后的 salary |
|---:|---:|
| 1 | 11000.00 |
| 2 | 8400.00 |
| 3 | 6300.00 |
| 7 | 11000.00 |

变更 3 行。`ELSE salary` 让其余等级保留原值。漏掉 `ELSE` 时，没匹配的分支会得到 `NULL`，可能触发非空约束。

## 四、控制批次和顺序

MySQL 单表 `UPDATE` 支持 `LIMIT`。单写 `LIMIT 2` 限制找到的匹配行数，但不会指定是哪两行。下面更新工资最低的两名在职员工。初始 `id=8`、`id=9` 工资同为 5000，用 `id` 作为最终排序键。若只取 1 行，也能明确先改 8。

```sql
START TRANSACTION;
SELECT id, salary FROM c4b_employees
WHERE status = 'active' ORDER BY salary, id LIMIT 2;

UPDATE c4b_employees SET salary = salary + 100.00
WHERE status = 'active'
ORDER BY salary, id LIMIT 2;

SELECT ROW_COUNT() AS changed_rows;
SELECT id, salary FROM c4b_employees WHERE id IN (8, 9) ORDER BY id;
ROLLBACK;
```

两人都得到 5100。`LIMIT` 对匹配的行计数，即使其中有的行设置前后值相同，也可能占掉批次名额。重复运行这种按可变工资排序的更新，可能再改同一行。真正批处理要用可重现的目标名单或能区分已处理状态的条件。

## 五、隔离实验：漏了 WHERE 会发生什么

下面是**特意写错的演示**。整块只作用于 `c4b_employees`，使用 InnoDB 事务，最后回滚并再次检查。别在其他查询标签或真实表上试。若客户端开启了安全更新，错误写法可能先收到 `1175`。这时直接执行 `ROLLBACK;`，并保留保护设置。

```sql
START TRANSACTION;
SELECT COUNT(*) AS rows_before, COUNT(DISTINCT salary) AS salaries_before
FROM c4b_employees;
UPDATE c4b_employees SET salary = 5000.00;
SELECT COUNT(*) AS rows_after, COUNT(DISTINCT salary) AS salaries_after,
       MIN(salary) AS min_salary, MAX(salary) AS max_salary
FROM c4b_employees;
ROLLBACK;
SELECT COUNT(*) AS rows_restored, COUNT(DISTINCT salary) AS salaries_restored
FROM c4b_employees;
```

依次是「9 行、7 种工资」「9 行、1 种工资，最低和最高都是 5000」「9 行、7 种工资」。行数一直是 9，所以只看片面行数会漏掉事故。若语句已经提交，需要经验证的备份或恢复方案，后来再运行 `ROLLBACK` 也收不回来。

## 小结

更新前核对目标、旧值及数量，更新后核对新值与边界行。对批次，加上能唯一确定顺序的键。重复执行可能扩大变更，先确认当前状态再重试。

## 动手练习

### 练习 1 · 只改其中一个周宁

把市场部周宁的等级改成 B，技术部周宁等级保持原样。先确定目标主键，再更新。

<details>
<summary>展开参考答案</summary>

```sql
SELECT id, department, grade FROM c4b_employees WHERE name = '周宁' ORDER BY id;
START TRANSACTION;
UPDATE c4b_employees SET grade = 'B' WHERE id = 9;
SELECT ROW_COUNT() AS changed_rows;
SELECT id, grade FROM c4b_employees WHERE id IN (2, 9) ORDER BY id;
ROLLBACK;
```

`id=9` 从 C 变 B，`id=2` 原本就是 B。两人同名，用主键定位。

</details>

### 练习 2 · 平手怎么选

给一名工资最低的在职员工加 50 元，工资相同的取 `id` 较小者。预测编号，写出预览和更新。

<details>
<summary>展开参考答案</summary>

```sql
START TRANSACTION;
SELECT id, salary FROM c4b_employees
WHERE status = 'active' ORDER BY salary, id LIMIT 1;
UPDATE c4b_employees SET salary = salary + 50.00
WHERE status = 'active' ORDER BY salary, id LIMIT 1;
SELECT id, salary FROM c4b_employees WHERE id IN (8, 9) ORDER BY id;
ROLLBACK;
```

8 变为 5050，9 仍为 5000。

</details>

### 练习 3 · 判断一次重试

一条 `salary = salary * 1.10` 超时了。你重连后为什么应该先检查结果？

<details>
<summary>展开参考答案</summary>

超时可能发生在提交前，也可能发生在提交已成功但客户端未收到结果之后。已提交时再加 10%，原工资 10000 会变成 12100。先核对变更目标、当前值和提交记录。

</details>

**下一篇**：[删除数据](03_DELETE删除.md)
