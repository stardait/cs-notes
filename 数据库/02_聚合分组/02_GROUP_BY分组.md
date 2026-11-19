# 第 02 章 · GROUP BY 分组

> 读到「每个部门」「每座城市」时，先把这几个字写成分组键。

## 学习目标

- 说明一行统计结果代表哪个组。
- 按单列、多个列或表达式分组，并明确结果顺序。
- 判断输出普通列时，是否能为每组确定唯一的值。

## 准备

```sql
USE learn;
SELECT COUNT(*) AS total FROM c2_employees;
```

仍是上一课 14 人的样本。技术部 4 人，市场部 3 人，财务部 3 人，人事部 4 人。每段查询用同一份数据。

## 一、每个部门各算一次

```sql
SELECT department, COUNT(*) AS employees,
       ROUND(AVG(salary), 2) AS average_salary
FROM c2_employees
GROUP BY department
ORDER BY average_salary DESC, department;
```

| department | employees | average_salary |
|---|---:|---:|
| 技术部 | 4 | 20250.00 |
| 财务部 | 3 | 11933.33 |
| 市场部 | 3 | 11833.33 |
| 人事部 | 4 | 7975.00 |

可以先把 14 行放进 4 个部门文件夹，再分别数每个文件夹里的行。结果一部门一行。预期输出顺序要用 `ORDER BY` 声明，`GROUP BY` 本身没有顺序保证。按实际平均值排名时可用 `ORDER BY AVG(salary) DESC` 保留舍入前的区别。

## 二、两列表示一个组合

```sql
SELECT department, city, COUNT(*) AS employees
FROM c2_employees
GROUP BY department, city
ORDER BY MIN(id);
```

这里一行表示一个曾出现的「部门、城市」组合，共 10 行。技术部在北京有 2 人，在深圳有 2 人，不会为它产生一行「杭州、0 人」。要显示不存在的组合，需要后续章节的多表查询。`ORDER BY MIN(id)` 按各组最小主键排序，组间顺序可确定。

## 三、每个工资档有几个人

```sql
SELECT salary DIV 5000 AS salary_band, COUNT(*) AS employees
FROM c2_employees
GROUP BY salary DIV 5000
ORDER BY salary_band;
```

`DIV` 是整数除法。这里工资非负，档位 1 表示 `[5000, 10000)`，档位 2 表示 `[10000, 15000)`，依此类推。5 个档位 `1, 2, 3, 4, 5` 的人数依次是 6、3、3、1、1。MySQL 支持在 `GROUP BY` 或 `HAVING` 中引用 `SELECT` 别名（避免与原列名重名）。这里保留原表达式，让分组依据更容易读。按入职年分组直接写 `GROUP BY hire_year`。

## 四、每组必须能回答输出的列

```sql
-- 预期错误 1055
SELECT department, name, MAX(salary) AS peak
FROM c2_employees
GROUP BY department;
```

同一部门有多个姓名，`MAX(salary)` 只返回最高工资值，其旁边的 `name` 没有唯一可推断的值。要求每组一行时，优先让输出由分组键和聚合函数组成。MySQL 也允许能由分组键唯一确定的列，例如按主键分组时同一键只有一个姓名。这个特例不适用于按部门分组。当前 `ONLY_FULL_GROUP_BY` 会拒绝有歧义的写法，保留它就能及时发现问题。

写成 `GROUP BY department, name` 会变成每「部门、姓名」一组，已经换了问题。如果想要整组的最高工资，省略姓名；如果要「最高工资的人是谁」，把那一步留到第 05 章或第 10 章。

## 小结

先定义一行是什么，再确定分组键。只算实际出现的组，并用 `ORDER BY` 明确你希望看到的顺序。

## 动手练习

### 练习 1 · 一部门一个奖金口径

每个部门显示人数、已知奖金人数、已知奖金平均值。技术部的三个数分别是多少？

<details>
<summary>展开参考答案</summary>

```sql
SELECT department, COUNT(*) AS employees, COUNT(bonus) AS known_bonus,
       ROUND(AVG(bonus), 2) AS average_known_bonus
FROM c2_employees GROUP BY department ORDER BY MIN(id);
```

技术部是 4 人、3 人、有数值的平均为 29000.00。

</details>

### 练习 2 · 找出现的组合

按部门和城市分组统计员工数，找技术部的两个组合。

<details>
<summary>展开参考答案</summary>

```sql
SELECT department, city, COUNT(*) AS employees
FROM c2_employees WHERE department = '技术部'
GROUP BY department, city ORDER BY MIN(id);
```

技术部 × 北京 2 人，技术部 × 深圳 2 人。

</details>

### 练习 3 · 最高值和对应人

为什么 `SELECT department, name, MAX(salary) … GROUP BY department` 行不通？如果只问最高工资怎么改？

<details>
<summary>展开参考答案</summary>

因为一个部门可以有多个姓名，最高工资数值本身也可能并列。只问数字时只保留部门和最高工资。

```sql
SELECT department, MAX(salary) AS peak FROM c2_employees GROUP BY department ORDER BY MIN(id);
```

</details>

**下一篇**：[HAVING 过滤分组](03_HAVING过滤分组.md)
