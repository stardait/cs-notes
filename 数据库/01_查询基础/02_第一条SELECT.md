# 第 1 章 · 第一条 SELECT

> 你现在有一张 `students` 表，5 行数据。这一篇就讲一件事：**怎么把这些数据「问」出来**。
>
> SELECT 不是「打印数据」，而是「描述我想要什么」——具体怎么取，数据库自己决定。

---

## 学习目标

1. 写出第一条 `SELECT`
2. 学会只取需要的列（而不是 `*`）
3. 给列起别名（`AS`）
4. 在查询里做计算

---

## 一、先看你的数据

打开 HeidiSQL，连上 MySQL，在查询窗口执行：

```sql
USE learn;
SELECT * FROM students;
```

你会看到：

| id | name | age | class | score | created_at |
|---|---|---|---|---|---|
| 1 | 小明 | 18 | 一班 | 92.50 | 2026-11-16 10:41:31 |
| 2 | 小红 | 17 | 一班 | 88.00 | 2026-11-16 10:41:31 |
| 3 | 小刚 | 19 | 二班 | 76.50 | 2026-11-16 10:41:31 |
| 4 | 小美 | 18 | 二班 | 95.00 | 2026-11-16 10:41:31 |
| 5 | 小强 | 17 | 一班 | 61.00 | 2026-11-16 10:41:31 |

---

## 二、SELECT 最少要写什么

### 最小的 SELECT

```sql
SELECT 1;
```

**结果**：

| 1 |
|---|
| 1 |

**这不查表，就是让数据库算个 1。** 用来测试连接、做计算器很方便。

> 💡 **重点**：`SELECT` 后面不一定跟表名。`SELECT` 的本意是「给我这个表达式的结果」。

---

### 查表：`SELECT ... FROM 表名`

```sql
SELECT * FROM students;
```

**拆开看**：

```
SELECT  *        FROM  students
  ↓     ↓          ↓      ↓
要什么  所有列    从哪    students 表
```

---

## 三、`*` 是通配符，但别总用它

`*` 表示「所有列」。**能跑，但不推荐。**

### 三个原因

**原因 1：性能浪费**

```sql
-- 你只想知道名字，却把 created_at 也读了出来
SELECT * FROM students;
```

**表有 50 列时，`SELECT *` 会把 50 列全传给你，你只用 2 列。**

**原因 2：程序会崩**

```
今天表结构：id, name, age, class, score
你的程序：按顺序取 5 个值 → 正常

明天同事加了 phone 列：id, name, age, class, score, phone
你的程序：按顺序取 5 个值 → 拿到的还是前 5 个，但顺序可能变
```

**写清楚列名，加列不影响你。**

**原因 3：可读性差**

```sql
-- 看不出来要什么
SELECT * FROM students;

-- 一眼看懂
SELECT name, score FROM students;
```

---

### 只取需要的列

**语法**：列名用逗号分隔

```sql
SELECT name, score FROM students;
```

**结果**：

| name | score |
|---|---|
| 小明 | 92.50 |
| 小红 | 88.00 |
| 小刚 | 76.50 |
| 小美 | 95.00 |
| 小强 | 61.00 |

> 💡 **重点**：`SELECT name, score` 里的列顺序，就是结果里的列顺序。写成 `SELECT score, name` 结果就倒过来。

---

## 四、给列起别名：`AS`

### 为什么需要别名

```sql
SELECT name, score FROM students;
```

结果是：

| name | score |
|---|---|
| 小明 | 92.50 |

**列名是英文的，看着不直观。** 改成中文：

```sql
SELECT name AS 姓名, score AS 分数 FROM students;
```

| 姓名 | 分数 |
|---|---|
| 小明 | 92.50 |

---

### 三种写法

**写法 1：`AS`（推荐）**

```sql
SELECT name AS 姓名 FROM students;
```

**写法 2：省略 `AS`**

```sql
SELECT name 姓名 FROM students;
```

**能跑，但可读性差，不推荐。**

**写法 3：带空格时用引号**

```sql
SELECT name AS `学生 姓名` FROM students;
```

**MySQL 用反引号**（键盘左上角，Tab 键上面那个）。

> ⚠️ **注意**：别用单引号！`SELECT name AS '姓名'` 在 MySQL 里会报错。单引号是给**字符串**用的。

---

## 五、计算列：可以在 SELECT 里做数学

**列不只是能选出来，还能算。**

```sql
SELECT name, score, score + 10 AS 加分后 FROM students;
```

**结果**：

| name | score | 加分后 |
|---|---|---|
| 小明 | 92.50 | 102.50 |
| 小红 | 88.00 | 98.00 |
| 小刚 | 76.50 | 86.50 |
| 小美 | 95.00 | 105.00 |
| 小强 | 61.00 | 71.00 |

**注意**：`score + 10` **不会修改表里的数据**，只是查询时算出来的一个「临时列」。

---

### 支持的计算

| 运算符 | 含义 | 例子 |
|---|---|---|
| `+` | 加 | `score + 10` |
| `-` | 减 | `score - 5` |
| `*` | 乘 | `score * 2` |
| `/` | 除 | `score / 2` |
| `%` | 取余 | `score % 10` |

---

### 实战例子

**场景 1：算总分**

```sql
SELECT name, score AS 原始分, score * 1.2 AS 加权后
FROM students;
```

**场景 2：算百分比**

```sql
SELECT name, score / 100 AS 百分比
FROM students;
```

**结果**：

| name | 百分比 |
|---|---|
| 小明 | 0.9250 |
| 小红 | 0.8800 |

**场景 3：组合字符串**

```sql
SELECT CONCAT(name, '（', class, '）') AS 学生信息
FROM students;
```

**结果**：

| 学生信息 |
|---|
| 小明（一班） |
| 小红（一班） |

`CONCAT` 是字符串拼接函数，后面第 6 章会细讲。

---

## 六、`DISTINCT`：去掉重复

**问题**：想知道有哪几个班级

```sql
SELECT class FROM students;
```

**结果**：

| class |
|---|
| 一班 |
| 一班 |
| 二班 |
| 二班 |
| 一班 |

**5 行，但只有 2 个班级。** 用 `DISTINCT` 去重：

```sql
SELECT DISTINCT class FROM students;
```

**结果**：

| class |
|---|
| 一班 |
| 二班 |

---

### `DISTINCT` 作用于整行

```sql
-- 会去重「班级+年龄」的组合
SELECT DISTINCT class, age FROM students;
```

**结果**：

| class | age |
|---|---|
| 一班 | 18 |
| 一班 | 17 |
| 二班 | 19 |
| 二班 | 18 |

**注意**：一班 18 岁出现了两次（小明），但去重后只留一条。

> ⚠️ **注意**：`DISTINCT` 要对**所有选出来的列**都相同的行才去重，不是只对第一列。

---

## 七、SQL 的书写规范

### 关键字大写

```sql
-- 好
SELECT name, score FROM students;

-- 能跑但不好读
select name, score from students;
```

**关键字大写、表名列名小写**，一眼分清谁是语法、谁是名字。

---

### 每个子句换行

**很短的可以一行**

```sql
SELECT name FROM students;
```

**有多个子句时换行**

```sql
SELECT name, score
FROM students;
```

---

### 加分号

```sql
SELECT name FROM students;
```

**MySQL 里执行单条语句可以不加**，但**加上是好习惯**（很多工具和脚本要求）。

---

### 注释

**单行**

```sql
-- 这是注释
SELECT name FROM students;
```

**多行**

```sql
/* 这是
   多行注释 */
SELECT name FROM students;
```

---

## 八、常见错误

### 错误 1：列名拼错

```sql
SELECT namee FROM students;
```

**报错**：

```
ERROR 1054 (42S22): Unknown column 'namee' in 'field list'
```

**解决**：先 `DESCRIBE students;` 看真实列名。

---

### 错误 2：表名拼错

```sql
SELECT * FROM student;
```

**报错**：

```
ERROR 1146 (42S02): Table 'learn.student' doesn't exist
```

**注意**：`students` 少了 `s` 就找不到。

**解决**：`SHOW TABLES;` 看有哪些表。

---

### 错误 3：忘记切换数据库

```sql
SELECT * FROM students;
```

**报错**：

```
ERROR 1046 (3D000): No database selected
```

**解决**：

```sql
USE learn;
```

或者在 HeidiSQL 里**双击左边的 `learn`**（让它变成粗体）。

---

### 错误 4：别名用单引号

```sql
SELECT name AS '姓名' FROM students;
```

**报错**（某些配置下）。

**正确**：

```sql
SELECT name AS 姓名 FROM students;
-- 或者
SELECT name AS `姓名` FROM students;
```

---

## 九、本章小结

### 完整语法

```sql
SELECT [DISTINCT] 列1 [AS 别名], 列2, 表达式
FROM 表名;
```

### 四个要点

| 要点 | 说明 |
|---|---|
| `*` 能用但别滥用 | 写清楚要哪几列 |
| `AS` 起别名 | 让结果更好读 |
| 计算列 | `score * 1.2`，不修改原数据 |
| `DISTINCT` | 去掉重复行 |

### 一条铁律

> **SELECT 只「读」，永不「改」数据。** 你怎么查都安全。

---

## 十、动手练习

**提示**：在 HeidiSQL 里直接写，按 `F9` 执行。

### 练习 1

查出所有学生的**姓名和年龄**。

（答案见文末 **答案 1**）

---

### 练习 2

查出所有学生的姓名、班级、分数，**列名用中文**。

（答案见文末 **答案 2**）

---

### 练习 3

查出所有学生，并显示一列「分数加 5 分后的值」。

（答案见文末 **答案 3**）

---

### 练习 4

查出这个班**一共有几种不同的年龄**。

（答案见文末 **答案 4**）

---

### 练习 5（挑战）

查出一个列表，显示「小明（一班）得了 92.5 分」这种格式的句子。

**提示**：`CONCAT` 可以拼接多个字符串。

（答案见文末 **答案 5**）

---

### 练习 6（思考题）

执行下面两条语句，结果有什么不同？为什么？

```sql
SELECT class, age FROM students;

SELECT DISTINCT class, age FROM students;
```

（答案见文末 **答案 6**）

---

## 十一、下一篇

现在你会「选列」了，但还不会「筛行」。

**下一篇**：[03_SELECT与WHERE.md](03_SELECT与WHERE.md) —— 用条件把想要的行挑出来。

---

## 附：在 HeidiSQL 里的操作小技巧

| 快捷键 | 作用 |
|---|---|
| `F9` | 执行当前 SQL |
| `Ctrl+T` | 新建查询标签 |
| `Ctrl+Shift+F4` | 关闭当前标签 |
| `Ctrl+滚轮` | 放大/缩小字体 |
| `Ctrl+/` | 注释/取消注释选中行 |

**只执行选中的部分**：选中几行 SQL，按 `F9`，只执行选中部分。方便一次写多条测试。


---

## 参考答案

> 先自己写，写完再对照。

### 答案 1

```sql
SELECT name, age FROM students;
```

### 答案 2

```sql
SELECT name AS 姓名, class AS 班级, score AS 分数 FROM students;
```

### 答案 3

```sql
SELECT name, score, score + 5 AS 加分后 FROM students;
```

### 答案 4

```sql
SELECT DISTINCT age FROM students;
```
结果是 17、18、19 三种。

### 答案 5

```sql
SELECT CONCAT(name, '（', class, '）得了 ', score, ' 分') AS 描述
FROM students;
```

### 答案 6

第一条有 5 行（每个人一行）。

第二条有 4 行——因为「一班+18 岁」组合出现了两次（小明和小美都是一班 18 岁），被去重了。

**关键**：`DISTINCT` 作用于**所有列的组合**，不是只对第一列。
