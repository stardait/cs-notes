# 第 01 章 · 第一条 SELECT

> 每写一条查询，先确定从哪张表取数据，再确定结果要长什么样。

## 学习目标

- 写出常量查询和查表查询，按需求选择输出列。
- 给结果列起别名、写计算列，预测 `DISTINCT` 去掉哪类重复。
- 看懂最常见的库名、表名和列名错误。

## 准备

```sql
USE learn;
SELECT id, name, age, class, score FROM students ORDER BY id;
```

基线 5 行。`SELECT` 只读取表；下面把结果排序写清楚，下一课后会专门学排序。

## 一、先决定结果的表头

```sql
SELECT 1 AS example_value, 2 + 3 AS total;
SELECT name, score FROM students ORDER BY id;
```

第一条没有 `FROM`，算出一行结果 `(1, 5)`。第二条从 `students` 取两列，按写出顺序显示。`SELECT * FROM students` 适合快速看一眼。日常查询更适合写出真正需要的列，阅读的人知道结果结构，不依赖表后续增加的列，也少传输无用信息。

## 二、别名和计算列

同一份成绩可以按报表需求呈现不同信息。`AS` 给结果列起名字，计算只发生在查询结果里。

```sql
SELECT name AS student_name,
       score AS original_score,
       score + 5 AS adjusted_score,
       score / 100 AS score_ratio
FROM students ORDER BY id;
```

小明一行原分是 92.50，计算列是 97.50 和 0.925（显示小数位可能更多）。重查 `students.score` 仍是 92.50。`AS` 可省略，保留它便于阅读。标识符含空格或要明示为列名时，可用反引号，例如 ``SELECT name AS `学生姓名` FROM students;``。普通文本值用单引号。MySQL 也接受在 `SELECT` 里用单引号声明别名，后续引用别名时单引号会解释成字符串，因此统一用反引号或简单名字。详见 [MySQL 列别名手册](https://dev.mysql.com/doc/refman/26.10/en/problems-with-alias.html)。

## 三、DISTINCT 看整组结果列

```sql
SELECT DISTINCT class FROM students ORDER BY class;
SELECT DISTINCT class, age FROM students ORDER BY class, age;
```

第一条出现 2 个班。第二条返回 4 个不同的「班级、年龄」组合。一班有 17、18 岁，二班有 18、19 岁。虽然 18 岁出现两次，属于不同班级时，两行的组合仍不相同。MySQL 文本排序以表达式的排序规则为准。

## 四、排查与书写

习惯把 `SELECT` 和 `FROM` 等大写，列名小写。多子句按行写，语句用分号结束。`-- `（两个连字符加空格）让该行后半部分成为注释。

```sql
-- 预期错误 1054
SELECT namee FROM students;
```

```sql
-- 预期错误 1146
SELECT name FROM learn.c1_missing_example;
```

1054 检查列名。1146 检查表名和库。1046 表示当前查询需要默认库但没选中。下面每道题都是独立查询。

## 小结

`FROM` 确定来源，`SELECT` 决定输出列，`AS` 给结果起名，`DISTINCT` 按所有输出列表达式去重。

## 动手练习

### 练习 1 · 只取报告要用的列

显示班级、姓名、成绩，按这个列顺序返回。

<details>
<summary>展开参考答案</summary>

```sql
SELECT class, name, score FROM students ORDER BY id;
```

返回 5 行，第一列为班级。

</details>

### 练习 2 · 计算列

输出姓名、原分和减去 60 后的分差。小强这一列是多少？

<details>
<summary>展开参考答案</summary>

```sql
SELECT name, score, score - 60 AS above_60 FROM students ORDER BY id;
```

小强 61 分，分差是 1。

</details>

### 练习 3 · 组合去重

只查不同年龄有几行？如果同时查班级和年龄呢？两次都用查询验证。

<details>
<summary>展开参考答案</summary>

```sql
SELECT DISTINCT age FROM students ORDER BY age;
SELECT DISTINCT class, age FROM students ORDER BY class, age;
```

第一条 3 行，第二条 4 行。

</details>

**下一篇**：[WHERE 条件筛选](03_SELECT与WHERE.md)
