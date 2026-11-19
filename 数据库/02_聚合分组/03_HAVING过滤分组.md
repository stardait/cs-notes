# 第 2 章 · HAVING —— 过滤分组结果

> 上一节你学会了 `GROUP BY`，把 14 个人压成了 4 个部门。现在你想：**只看「平均工资超过 15000 的部门」**。
>
> 条件塞进 `WHERE`，报错了。不是你写错了，是**位置错了**——`WHERE` 管的是「行」，那时还没分组；要筛「组」，得用 `HAVING`。
>
> 记住这一句，这辈子不会用错：**`WHERE` 管行，`HAVING` 管组。**

---

## 学习目标

1. 知道 `HAVING` 是什么：对 `GROUP BY` 之后的结果过滤
2. 彻底分清 `WHERE` 和 `HAVING`（本篇重点）
3. 背下执行顺序：`FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`
4. 理解「为什么 `WHERE` 里不能用聚合函数」，并会让两者配合（先筛行，再筛组）
5. 知道「取每组前 N 名」为什么不能只靠 `HAVING`

---

## 准备：造演示数据

本篇的演示表建在 **`learn`** 库里，表名加 `c2_` 前缀，和同章其他篇的表一眼就能分开，也不会碰你自己的 `students` 表。

复制下面整段到 HeidiSQL，按 `F9` 执行：

```sql
USE learn;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS c2_employees;
CREATE TABLE c2_employees (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(50)  NOT NULL,
    department  VARCHAR(20)  NOT NULL,
    city        VARCHAR(20),
    salary      DECIMAL(10,2),
    bonus       DECIMAL(10,2),
    hire_year   INT
);

INSERT INTO c2_employees (name, department, city, salary, bonus, hire_year) VALUES
    ('张伟', '技术部', '北京', 28000, 30000, 2019),
    ('李娜', '技术部', '北京', 22000,   NULL, 2021),
    ('王强', '技术部', '杭州', 18000, 12000, 2020),
    ('刘洋', '技术部', '北京', 15000,   NULL, 2023),
    ('陈静', '市场部', '上海', 16000,  8000, 2018),
    ('杨帆', '市场部', '上海',  9000,   NULL, 2022),
    ('赵敏', '市场部', '广州', 12000,  5000, 2020),
    ('周杰', '市场部', '上海',  7500,  3000, 2024),
    ('孙丽', '财务部', '北京', 14000,  6000, 2015),
    ('吴涛', '财务部', '北京', 11000,   NULL, 2019),
    ('郑华', '财务部', '杭州',  8000,  4000, 2023),
    ('冯霞', '人事部', '上海',  9500,  3500, 2016),
    ('何磊', '人事部', '上海',  7000,   NULL, 2021),
    ('罗婷', '人事部', '广州',  6000,  2000, 2024);

SET FOREIGN_KEY_CHECKS = 1;
```

**执行完，`learn` 库里会多出 `c2_employees` 表，14 行，4 个部门**：技术部 4 人、市场部 4 人、财务部 3 人、人事部 3 人。**有 5 行的 `bonus` 是 NULL**（李娜、刘洋、杨帆、吴涛、何磊，第 5 节会用到）。

> 💡 **重点**：这篇之后的所有 SQL，都要先 `USE learn;`（或在 HeidiSQL 里双击 `learn` 库，让它变粗体）。

---

## 一、HAVING 是什么：对分组结果再筛一次

> 💡 **一句话点破**：`HAVING` 不筛「行」，它筛「组」——分组完成后，把不合格的**整组**扔掉。

先看 `GROUP BY` 能做到哪一步：

```sql
SELECT department, COUNT(*) AS 人数, AVG(salary) AS 平均工资
FROM c2_employees
GROUP BY department;
```

| department | 人数 | 平均工资 |
|---|---|---|
| 技术部 | 4 | 20750.000000 |
| 市场部 | 4 | 11125.000000 |
| 财务部 | 3 | 11000.000000 |
| 人事部 | 3 | 7500.000000 |

14 行压成 4 行。现在加 `HAVING`：

```sql
SELECT department, AVG(salary) AS 平均工资
FROM c2_employees
GROUP BY department
HAVING AVG(salary) > 15000;
```

| department | 平均工资 |
|---|---|
| 技术部 | 20750.000000 |

**4 组只剩 1 组。** 市场部、财务部、人事部**整组被扔掉**——不是扔掉组里某几个人，是整个部门不要了。语法上 `HAVING` 必须写在 `GROUP BY` 之后，它判断的是**组的条件**，不是行的条件。

**生活类比：公司季度评优。** HR 先把人按部门分组（`GROUP BY`），算出每组平均绩效（`AVG`），再规定「平均绩效不到 15000 的部门整组出局」（`HAVING`）。淘汰的是**整个部门**，不是某个人。

> 💡 **重点**：`HAVING` 的判断单位是「组」，它没法只留下某一组里的某几行。

---

## 二、完整执行顺序：本篇最重要的一张图

**你写的顺序**是 `SELECT → FROM → WHERE → GROUP BY → HAVING`；**数据库实际执行的顺序**是：

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

| 步 | 关键字 | 干什么 | 数据形态 |
|---|---|---|---|
| 1 | `FROM` | 找到表 | 14 行明细 |
| 2 | `WHERE` | 筛**行** | 还是行，变少了 |
| 3 | `GROUP BY` | 把行**压成组** | 变成 4 组 |
| 4 | `HAVING` | 筛**组** | 还是组，变少了 |
| 5 | `SELECT` | 选列、算别名 | 组 → 结果行 |
| 6 | `ORDER BY` | 排序 | 顺序变了 |
| 7 | `LIMIT` | 限条数 | 行数变少 |

这张图能解释三件事：`WHERE` 里不能写 `AVG()`（第 2 步还没分组）；`WHERE` 不能用 `SELECT` 别名（第 5 步还没执行）；`HAVING` 能用聚合函数（第 4 步时组已存在）。

> 💡 **重点**：`GROUP BY` 在第 3 步，`HAVING` 在第 4 步——**先有组，才能筛组**。

---

## 三、🔴 WHERE vs HAVING：核心区别（本篇重点）

> 💡 **一句话点破**：`WHERE` 管行，`HAVING` 管组。`WHERE` 在分组前，`HAVING` 在分组后。

| | `WHERE` | `HAVING` |
|---|---|---|
| 过滤对象 | **行**（单条记录） | **组**（分组结果） |
| 执行时机 | `GROUP BY` **之前** | `GROUP BY` **之后** |
| 能用聚合函数 | ❌ 不能 | ✅ 能 |
| 能用普通列 | ✅ 能 | ⚠️ 只能用**分组列** |
| 能用 `SELECT` 别名 | ❌ 不能 | ⚠️ MySQL 里可以（非标准） |
| 不写 `GROUP BY` 时 | 正常工作 | 把整张表当 1 组 |

**不用背。记住口诀 + 执行顺序图，随时能推出来。** 看个容易误导的例子——需求是「找出有员工工资超过 25000 的部门，显示部门和人数」：

**写法 A：条件写 `WHERE`**

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
WHERE salary > 25000
GROUP BY department;
```

结果 1 行：技术部 **1 人**。**人数是 1！** `WHERE` 先把 13 个工资不过 25000 的人删掉，技术部**只剩张伟一个人**，再分组自然数出 1。

**写法 B：条件写 `HAVING`**——只把 `WHERE` 那两行换成 `HAVING MAX(salary) > 25000`：

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
GROUP BY department
HAVING MAX(salary) > 25000;
```

| department | 人数 |
|---|---|
| 技术部 | 4 |

**人数是 4！** 先完整分组（技术部 4 人），再判断「这组最高工资有没有超过 25000」，通过就**整组保留**。

> ⚠️ **注意**：这**不是**同一个问题的两种写法，是**两个不同的问题**！A 问「工资超 25000 的这些人按部门怎么分布」，B 问「哪些部门里有人工资超 25000，这些部门一共多少人」。

**生活类比：筛水果。** `WHERE` 是洗的时候**把烂苹果挑掉**（挑单个苹果）；`HAVING` 是装袋后**称重，不够 1 斤的整袋不要**（挑整袋）。顺序不能反。

---

## 四、为什么 WHERE 里不能用聚合函数

```sql
SELECT department, AVG(salary)
FROM c2_employees
WHERE AVG(salary) > 10000
GROUP BY department;
```

**报错**：`ERROR 1111 (HY000): Invalid use of group function`

**翻译：分组函数（聚合函数）用错位置了。** 因为 `WHERE` 在第 2 步（`FROM → WHERE → ...`），`GROUP BY` 在第 3 步——`WHERE` 执行时 `GROUP BY` 还没发生。**没有分组，「每组平均工资」这个概念根本不存在**，数据库不知道你说的是谁的平均值。

**类比**：老师说「把每个班平均分大于 90 的班留下来」。你得**先按班分组**才能算每班平均分，才能判断。连班都还没分，手上只有一叠混在一起的成绩单——「每班平均分」此刻是无意义的。

**正确写法**：条件移到 `HAVING`。

```sql
SELECT department, AVG(salary) AS 平均工资
FROM c2_employees
GROUP BY department
HAVING AVG(salary) > 10000;
```

| department | 平均工资 |
|---|---|
| 技术部 | 20750.000000 |
| 市场部 | 11125.000000 |
| 财务部 | 11000.000000 |

**3 组通过，人事部（7500）被扔掉。**

> 💡 **重点**：**只要条件里出现聚合函数（`AVG` `SUM` `COUNT` `MAX` `MIN`），就必须写在 `HAVING` 里。** 没有例外。不写 `GROUP BY` 时整张表当 1 组，`HAVING AVG(salary) > 10000` 返回全公司平均 13071.428571（1 行）；改成 `> 20000` 返回 0 行。

---

## 五、HAVING 里能写什么

`HAVING` 里只允许三类东西：① 聚合函数（`HAVING AVG(salary) > 15000`）；② 分组列（`HAVING department = '技术部'`）；③ 两者组合。

### ① 聚合函数：最常用

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
GROUP BY department
HAVING COUNT(*) >= 4;
```

结果 2 行：技术部 4 人、市场部 4 人。

```sql
SELECT department, COUNT(bonus) AS 有奖金人数, ROUND(AVG(bonus), 2) AS 平均奖金
FROM c2_employees
GROUP BY department
HAVING AVG(bonus) > 5000;
```

| department | 有奖金人数 | 平均奖金 |
|---|---|---|
| 技术部 | 2 | 21000.00 |
| 市场部 | 3 | 5333.33 |

> ⚠️ **注意**：`AVG(bonus)` 的分母是 `COUNT(bonus)`（有奖金的人数），**不是 `COUNT(*)`（总人数）**。技术部 4 人里只有 2 人有奖金，平均按 2 人算：(30000+12000)/2 = 21000。同理 `HAVING SUM(bonus) > 15000` 会留下技术部（42000）和市场部（16000）——`SUM` 也忽略 NULL。

### ② 分组列：能写，但建议放 `WHERE`

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
WHERE department IN ('技术部', '财务部')
GROUP BY department;
```

结果 2 行：技术部 4 人、财务部 3 人。把 `WHERE` 换成 `HAVING department IN ('技术部', '财务部')`，结果**完全一样**。

> 💡 **重点**：**分组列的条件优先写 `WHERE`。** `WHERE` 在分组**之前**就筛掉行，后面要分组的行更少；写 `HAVING` 等于先分好组再扔掉几组，白干活。数据量小感觉不到，数据量大差很多。

### ③ 不能写：非分组、非聚合的列

```sql
SELECT department, AVG(salary)
FROM c2_employees
GROUP BY department
HAVING city = '北京';
```

报错 `ERROR 1054 (42S22): Unknown column 'city' in 'having clause'`。**为什么**：按部门分组后，技术部这一组 4 个人的城市分别是北京、北京、杭州、北京——**两个城市**，`city` 在一组里有多个值，`HAVING` 拿哪个去比？数据库拒绝回答这个没意义的问题。

> ⚠️ **注意**：`HAVING` 里只能出现「**分组列**」或「**聚合值**」。`name`、`city`、`salary` 这类普通列一概不行。想按城市筛：要么把 `city` 加进 `GROUP BY`，要么把条件写进 `WHERE`。

### MySQL 的小福利：`HAVING` 能用别名

```sql
SELECT department, ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees
GROUP BY department
HAVING 平均工资 > 15000;
```

结果 1 行：技术部 20750.00。但同样的别名写进 `WHERE` 就报错（`ERROR 1054: Unknown column '平均工资' in 'where clause'`）——`WHERE` 在 `SELECT` 之前执行，别名还没诞生。

> ⚠️ **注意**：`HAVING` 用别名是 **MySQL 扩展**，标准 SQL 和 PostgreSQL 都不支持。为了可移植，`HAVING` 里建议把表达式完整写一遍。

---

## 六、WHERE + GROUP BY + HAVING 三个一起用

> 💡 **一句话点破**：`WHERE` 先筛「人」，`GROUP BY` 再分组，`HAVING` 最后筛「组」——**三层漏斗**。

**需求**：只看工资超 12000 的人，按部门算平均，再留下平均工资超 15000 的部门。

```sql
SELECT department, COUNT(*) AS 人数, AVG(salary) AS 平均工资
FROM c2_employees
WHERE salary > 12000
GROUP BY department
HAVING AVG(salary) > 15000;
```

| department | 人数 | 平均工资 |
|---|---|---|
| 技术部 | 4 | 20750.000000 |
| 市场部 | 1 | 16000.000000 |

**数据怎么变少**：`FROM` 取 14 行 → `WHERE` 筛掉 8 人剩 6 行 → `GROUP BY` 压成 3 组（技术部 4 人/20750、市场部 1 人/16000、财务部 1 人/14000）→ `HAVING` 淘汰财务部（14000），剩 2 组。

### 🔴 关键：`WHERE` 会改变 `HAVING` 看到的数据

**把上面两行删掉、不写 `WHERE`**，同样的查询只剩技术部 1 行（4 人，20750）。

**市场部没了！** 不筛人时市场部 4 人平均只有 11125，达不到 15000。**加上 `WHERE salary > 12000` 后，市场部只剩陈静一个人（16000）**，平均变 16000，于是通过了。

> 🔴 **重点**：`WHERE` 和 `HAVING` 不是「同一个筛子换个地方放」。**先筛行会改变每组的成员，也就改变了 `AVG` / `COUNT` / `SUM` 的结果。**

**生活类比：三层筛选线。** 一箱苹果先按大小挑出能卖的（`WHERE` 筛单个），再按品种装箱（`GROUP BY` 分组），最后整箱称重，不达标的整箱退货（`HAVING` 筛整箱）。

---

## 七、取每组前 N 名：`HAVING` 做不到

**需求**：每个部门工资最高的 2 个人。

**为什么 `HAVING` 不行**？因为它决定的是「整组留不留」，**没法只留组里的某几行**。技术部这组有张伟 28000、李娜 22000、王强 18000、刘洋 15000，你想要张伟和李娜——但 `HAVING` 只能二选一：✅ 整组保留（4 人全要）／❌ 整组扔掉（4 人全不要），做不到「留 2 个、扔 2 个」。

> 💡 **重点**：`HAVING` 的粒度是「组」，`WHERE` 的粒度是「行」，而「每组前 N 名」要求**以组为单位挑行**——两个工具都干不了，得用子查询或窗口函数。

### 办法 1：相关子查询

**思路**：对每个人，数一数「同部门里工资比我高的有几个人」。比我高的少于 2 个，我就是前 2 名。

```sql
SELECT e.department, e.name, e.salary
FROM c2_employees e
WHERE (
    SELECT COUNT(*)
    FROM c2_employees x
    WHERE x.department = e.department
      AND x.salary > e.salary
) < 2
ORDER BY e.department, e.salary DESC;
```

| department | name | salary |
|---|---|---|
| 人事部 | 冯霞 | 9500.00 |
| 人事部 | 何磊 | 7000.00 |
| 市场部 | 陈静 | 16000.00 |
| 市场部 | 赵敏 | 12000.00 |
| 技术部 | 张伟 | 28000.00 |
| 技术部 | 李娜 | 22000.00 |
| 财务部 | 孙丽 | 14000.00 |
| 财务部 | 吴涛 | 11000.00 |

**8 行 = 4 个部门 × 2 人。** 以王强（技术部 18000）为例：同部门比他高的有张伟、李娜共 2 个，`2 < 2` 不成立，被排除。张伟最高，比他高的 0 个，留下。

### 办法 2：窗口函数（MySQL 8.0+）

```sql
SELECT department, name, salary
FROM (
    SELECT department, name, salary,
           ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM c2_employees
) t
WHERE rn <= 2
ORDER BY department, salary DESC;
```

**结果和上面完全一样（8 行）。** `ROW_NUMBER()` 按部门分窗、窗口内按工资降序编号——技术部张伟 rn=1、李娜 rn=2、王强 rn=3、刘洋 rn=4。外层 `WHERE rn <= 2` 筛的是子查询产生的「行」，所以能用 `WHERE`。

> ⚠️ **注意**：这两种写法本篇只要「看懂思路」。子查询在第 3 章细讲，窗口函数在进阶篇细讲。要记住：**`HAVING` 解决「整组要不要」，解决不了「组内取前 N」。**

### 顺带说说 `LIMIT` 为什么也不行
`ORDER BY salary DESC LIMIT 2` 返回张伟（28000）、李娜（22000）。**看着对了，其实是巧合**——全公司最高工资前 2 名恰好都是技术部的。`LIMIT 2` 限制的是**整个结果集**，不认分组边界；换成 `LIMIT 5` 就露馅了：张伟 28000、李娜 22000、王强 18000、**陈静 16000（市场部）**、刘洋 15000——技术部占 4 个，市场部也混进来一个，根本不是「每个部门各取 5 个」。

> 🔴 **重点**：`LIMIT` 也实现不了「每组前 N」，因为它的作用域是最终结果。

---

## 八、常见错误

> ⚠️ **【常见错误】** 下面三条几乎每个人都会踩一遍，见到报错先回来对一遍。

### 错误 1：该用 `HAVING` 却写了 `WHERE`（最常见）

```sql
-- ❌ 报错
SELECT department, AVG(salary) AS 平均工资
FROM c2_employees
WHERE AVG(salary) > 15000
GROUP BY department;
```

**报错**：`ERROR 1111 (HY000): Invalid use of group function`

**为什么会犯**：上一篇刚学 `WHERE`，习惯性把条件都往 `WHERE` 里塞。判断口诀：条件里有 `AVG` / `SUM` / `COUNT` / `MAX` / `MIN` → 写 `HAVING`；条件只涉及单个行里的列 → 优先写 `WHERE`。**改法**：条件移到 `HAVING`（结果：技术部 20750，1 行）。

### 错误 2：`HAVING` 里用了非分组、非聚合的列

```sql
-- ❌ 报错：Unknown column 'city' in 'having clause'
SELECT department, AVG(salary)
FROM c2_employees
GROUP BY department
HAVING city = '北京';
```

**两种正确改法，含义不同**：改法 1 把 `city` 加进 `GROUP BY`，按「部门+城市」分组，结果 2 行（技术部/北京 3 人、财务部/北京 2 人）；改法 2 把条件放进 `WHERE`，分组前先筛掉别的城市，结果 2 行（技术部 3 人、财务部 2 人）。**人数一样，含义不同**——改法 1 的结果里带着 `city` 列。

> ⚠️ **注意**：`ONLY_FULL_GROUP_BY` 模式下这里会直接报错，这是好事。某些宽松配置的 MySQL 可能**不报错，而随便拿组里某一行的 `city` 去比**——对错全看运气，那才最危险。

### 错误 3：`HAVING` 写在 `GROUP BY` 前面

```sql
-- ❌ 报错
SELECT department, COUNT(*)
FROM c2_employees
HAVING COUNT(*) > 3
GROUP BY department;
```

**报错**：`ERROR 1064 (42000): ... near 'GROUP BY department' at line 5`

**为什么**：SQL 的**书写顺序是固定的**。虽然执行顺序里 `HAVING` 在 `GROUP BY` 之后，但写的时候 `GROUP BY` 必须在 `HAVING` 前面——照这个顺序写就不会错：`SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT`。

---

## 本章小结

> 💡 **一句话核心**：`WHERE` 管行，`HAVING` 管组。

`FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`

**判断规则**：有聚合函数 → `HAVING`；只有单个行的列 → `WHERE`；分组列的条件 → 优先 `WHERE`（更早筛掉，性能更好）。

**必须记住三个点**：① `WHERE` 里写聚合函数会报 `ERROR 1111`（那时还没分组）；② `HAVING` 里只能用「分组列」或「聚合值」（其他列报 `ERROR 1054`）；③ `HAVING` 只能决定整组留不留，做不到「每组取前 N」（要用子查询或窗口函数）。

---

## 动手练习

**提示**：先 `USE learn;`，在 HeidiSQL 里写，按 `F9` 执行。

### 练习 1

查出每个部门的平均工资，只显示平均工资**超过 10000** 的部门。（答案见文末 **答案 1**）

### 练习 2

查出**人数大于等于 4** 的部门，显示部门名和人数。（答案见文末 **答案 2**）

### 练习 3

查出**奖金总额超过 20000** 的部门，显示部门名和奖金总额。（答案见文末 **答案 3**）

### 练习 4

查出**平均工资超过全公司平均工资**的部门。提示：全公司平均要用子查询算，写成 `(SELECT AVG(salary) FROM c2_employees)`。（答案见文末 **答案 4**）

### 练习 5（先筛行再筛组）

只看**入职年份在 2020 年及以前**的员工，按部门算平均工资，**留下平均工资超过 12000** 的部门。（答案见文末 **答案 5**）

### 练习 6（陷阱题）

下面这条 SQL 想查「每个部门里工资超过 20000 的人有几个」：

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
WHERE salary > 20000
GROUP BY department
HAVING COUNT(*) >= 1;
```

如果把 `WHERE salary > 20000` 那一行**删掉**，条件挪进 `HAVING`，写成 `HAVING AVG(salary) > 20000`，人数变成几个？为什么不是同一个问题？（答案见文末 **答案 6**）

---

## 参考答案

> 先自己写，写完再对照。

### 答案 1

```sql
SELECT department, AVG(salary) AS 平均工资
FROM c2_employees
GROUP BY department
HAVING AVG(salary) > 10000;
```

结果 3 行：技术部（20750）、市场部（11125）、财务部（11000）。人事部 7500 被淘汰。

### 答案 2

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
GROUP BY department
HAVING COUNT(*) >= 4;
```

结果 2 行：技术部 4 人、市场部 4 人。写成 `WHERE COUNT(*) >= 4` 会报 `ERROR 1111`。

### 答案 3

```sql
SELECT department, SUM(bonus) AS 奖金总额
FROM c2_employees
GROUP BY department
HAVING SUM(bonus) > 20000;
```

结果 1 行：技术部 42000。市场部只有 16000（8000+5000+3000），不到 20000。

### 答案 4

```sql
SELECT department, AVG(salary) AS 平均工资
FROM c2_employees
GROUP BY department
HAVING AVG(salary) > (SELECT AVG(salary) FROM c2_employees);
```

全公司平均 13071.43，只有技术部（20750）超过它。

### 答案 5

```sql
SELECT department, COUNT(*) AS 人数, AVG(salary) AS 平均工资
FROM c2_employees
WHERE hire_year <= 2020
GROUP BY department
HAVING AVG(salary) > 12000;
```

结果 3 行：技术部（2 人，23000）、市场部（2 人，14000）、财务部（2 人，12500）。

**拆开算**：技术部留下张伟（2019, 28000）、王强（2020, 18000），李娜（2021）、刘洋（2023）被 `WHERE` 筛掉；市场部留下陈静（2018, 16000）、赵敏（2020, 12000）；财务部留下孙丽（2015, 14000）、吴涛（2019, 11000）；人事部只剩冯霞（2016, 9500），不到 12000，被 `HAVING` 淘汰。

### 答案 6

**不一样。** 原句先筛人再分组：`WHERE salary > 20000` 只剩张伟（28000）、李娜（22000），技术部 **2 人**。把 `WHERE` 删掉、条件改写成 `HAVING AVG(salary) > 20000` 后，是**先完整分组再算平均**：技术部 (28000+22000+18000+15000)/4 = 20750 > 20000 通过；市场部 11125、财务部 11000、人事部 7500 都不通过，所以是技术部 **4 人**。

**一个是「工资超 20000 的人有几个」，一个是「平均工资超 20000 的部门里一共有几个人」——完全不同的问题。**

---

## 下一篇

第 2 章就快学完了。你现在能：用聚合函数把多行压成一行、用 `GROUP BY` 分组、用 `HAVING` 过滤分组结果、分清 `WHERE` 和 `HAVING`。**下一篇是本章综合练习**——把前三篇混在一起，出 12 道统计题。

**下一篇**：[04_综合练习.md](04_综合练习.md)
