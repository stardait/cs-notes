# 第 2 章 · GROUP BY —— 把行分成若干组

> 用上一篇学的聚合函数，本篇这 14 行会压成 1 行：全公司平均工资 **14178.57**——一个数字，回答的是「全公司」。
>
> 但老板问的是「**每个部门**平均多少」——一个数字回答不了「每个」的问题。
>
> `GROUP BY` 就是干这个的：**先把行按某个列的值分成若干堆，再在每堆里各算一次聚合。**

---

## 学习目标

1. 说清 `GROUP BY` 在干什么：**分堆**，不是排序、不是去重
2. 单列分组：每个部门的平均工资
3. 多列分组：每个部门 + 每个城市的平均工资
4. 分组后 `SELECT` 只能写「分组列 + 聚合函数」
5. 看懂 `ERROR 1055`，避开「SELECT 未分组列」的坑
6. 用 `ORDER BY` 给统计结果排序
7. 用表达式分组（按入职年份、按工资区间）
8. 认清「按别名分组」的兼容性陷阱

---

## 准备：造演示数据

本篇的所有表都建在 **`learn`** 库里，表名加 `c2_` 前缀，不会碰你自己的 `students` 表。

14 个员工，**故意留了 4 行 `bonus` 是 NULL**——这是本篇最重要的教学道具。

复制下面整段到 HeidiSQL，按 `F9` 执行：

```sql
USE learn;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS c2_employees;
CREATE TABLE c2_employees (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(50)  NOT NULL,
    department  VARCHAR(20)  NOT NULL,   -- 部门
    city        VARCHAR(20),             -- 城市（周雨这行留 NULL）
    salary      DECIMAL(10,2),           -- 工资
    bonus       DECIMAL(10,2),           -- 奖金（4 行是 NULL）
    hire_year   INT                      -- 入职年份
);

INSERT INTO c2_employees (name, department, city, salary, bonus, hire_year) VALUES
    ('张伟', '技术部', '北京', 28000, 30000, 2019),
    ('李静', '技术部', '北京', 22000, 15000, 2019),
    ('王强', '技术部', '上海', 30000, NULL,  2016),
    ('赵敏', '技术部', '上海', 18000, 8000,  2022),
    ('刘洋', '市场部', '北京', 12000, 5000,  2020),
    ('陈晨', '市场部', '北京', 15000, NULL,  2018),
    ('杨帆', '市场部', '广州', 9000,  3000,  2022),
    ('周雨', '市场部', NULL,   11000, NULL,  2024),
    ('吴磊', '财务部', '北京', 10000, 6000,  2016),
    ('郑爽', '财务部', '上海', 13000, 4000,  2019),
    ('孙丽', '财务部', '上海', 8000,  NULL,  2015),
    ('马超', '人事部', '北京', 7000,  2000,  2019),
    ('林芳', '人事部', '广州', 6000,  1000,  2020),
    ('何军', '人事部', '广州', 9500,  2500,  2016);

SET FOREIGN_KEY_CHECKS = 1;
```

**执行完，`learn` 库里会多出 `c2_employees` 表，里面有 14 行数据。**

> 💡 **重点**：这篇后面所有 SQL 都要先 `USE learn;`（或在 HeidiSQL 里双击 `learn` 库，让它变粗体）。

**先看一眼这 14 行**（`SELECT * FROM c2_employees;`）。记住三个细节，后面全用得上：`bonus` 有 4 行是 NULL（王强、陈晨、周雨、孙丽），`city` 有 1 行是 NULL（周雨），14 人分属 4 个部门、北京/上海/广州三个城市。

---

## 一、GROUP BY 是什么：14 行变 4 行

**一句话点破：`GROUP BY` 按某一列的值把行分成若干堆，聚合函数在每堆里各算一次。**

```sql
SELECT COUNT(*) AS 人数, ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees;
```

| 人数 | 平均工资 |
|---|---|
| 14 | 14178.57 |

**14 行压成 1 行。** 这是上一篇聚合函数的本事——但它只能回答「全公司」的问题。想看「每个部门」，就得先分堆：

```sql
SELECT department, COUNT(*) AS 人数
FROM c2_employees
GROUP BY department;
```

| department | 人数 |
|---|---|
| 技术部 | 4 |
| 市场部 | 4 |
| 财务部 | 3 |
| 人事部 | 3 |

**14 行 → 4 行。** 14 行按 `department` 的值分成了 4 堆，`COUNT(*)` 在每堆里各数一次。

> 💡 **重点**：`GROUP BY` 是**分堆**：按某一列的值把行分成若干组，聚合函数在每组里单独算。**结果行数 = 组的个数**，不是原表的行数。

**一个类比**：一副牌 52 张，你想知道「每种花色有几张」。你不是去数 52 张，而是先按花色分成 4 堆，再数每堆几张。`GROUP BY` 就是「按花色分堆」，`COUNT(*)` 是「数每堆几张」。

**执行顺序**：`FROM → WHERE → GROUP BY（分堆）→ 聚合 → HAVING → SELECT → ORDER BY → LIMIT`

> 💡 **重点**：`GROUP BY` 在 `SELECT` **之前**执行。记住这点，第五节「为什么 SELECT 里不能写 name」就自然懂了。

---

## 二、单列分组：每个部门的平均工资

**一句话点破：按 `department` 分堆，每堆算一次 `AVG`。**

```sql
SELECT department, COUNT(*) AS 人数,
       ROUND(AVG(salary), 2) AS 平均工资, SUM(salary) AS 工资合计
FROM c2_employees
GROUP BY department;
```

| department | 人数 | 平均工资 | 工资合计 |
|---|---|---|---|
| 技术部 | 4 | 24500.00 | 98000.00 |
| 市场部 | 4 | 11750.00 | 47000.00 |
| 财务部 | 3 | 10333.33 | 31000.00 |
| 人事部 | 3 | 7500.00 | 22500.00 |

以技术部为例：4 行是 28000、22000、30000、18000；`AVG` = 98000 / 4 = **24500.00**，`SUM` = 98000。

> ⚠️ **注意**：结果只有 4 行，原来 14 行明细被「压缩」掉了——每行代表一个**组**，不是一个人。而且这个顺序只是**碰巧**（碰巧是插入顺序），`GROUP BY` 不保证顺序，要排序看第六节。

> ❌ **常见错误**：把 4 行结果当成「4 个员工」。每行是一个部门统计值，`平均工资` 不是任何一个人的工资。

---

## 三、多列分组：每个部门、每个城市的平均工资

**一句话点破：`GROUP BY` 后面写几列，就按几个列的值组合分堆。**

```sql
SELECT department, city, COUNT(*) AS 人数,
       ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees
GROUP BY department, city;
```

| department | city | 人数 | 平均工资 |
|---|---|---|---|
| 技术部 | 北京 | 2 | 25000.00 |
| 技术部 | 上海 | 2 | 24000.00 |
| 市场部 | 北京 | 2 | 13500.00 |
| 市场部 | 广州 | 1 | 9000.00 |
| 市场部 | NULL | 1 | 11000.00 |
| 财务部 | 北京 | 1 | 10000.00 |
| 财务部 | 上海 | 2 | 10500.00 |
| 人事部 | 北京 | 1 | 7000.00 |
| 人事部 | 广州 | 2 | 7750.00 |

**4 组变成 9 组。** 「部门」这一层不够细了：技术部在北京、上海各 2 人，是两个不同的组。

**组数不是乘出来的。** 4 个部门 × 4 个城市值（北京、上海、广州、NULL）≠ 16 组——很多组合根本没人，只保留**真实出现过的组合**。

> ⚠️ **注意**：看到 `市场部 | NULL` 那一行了吗？**`GROUP BY` 会把所有 NULL 归成一组。** 这和第 1 章「`WHERE city = NULL` 匹配不到任何行」不矛盾：`WHERE` 里 `NULL = NULL` 不成立，但 `GROUP BY` 是「把相同的值放一起」，NULL 和 NULL 算同一堆。

> 💡 **重点**：多列分组 = 按**组合**分堆。结果行数 = 真实出现过的组合数。

---

## 四、分组后 SELECT 里能写什么

**一句话点破：分组后每一行代表一个「组」，所以 `SELECT` 里只能写「组里统一的东西」。**

| 写法 | 例子 | 允许？ |
|---|---|---|
| `GROUP BY` 里出现的列 | `department`、`city` | ✅ |
| 聚合函数 | `COUNT(*)`、`AVG(salary)` | ✅ |
| 常量 | `'2026 年'` | ✅ |
| 由上面几样组成的表达式 | `ROUND(AVG(salary), 2)` | ✅ |
| 没分组的普通列 | `name`、`salary` | ❌ 报错 |
| 没分组列组成的表达式 | `salary * 1.2` | ❌ 报错 |
| 聚合函数套聚合函数 | `MAX(AVG(salary))` | ❌ 报错 |

```sql
SELECT department, COUNT(*) AS 人数, COUNT(bonus) AS 有奖金人数,
       ROUND(AVG(bonus), 2) AS 平均奖金, '2026 年' AS 统计年份
FROM c2_employees
GROUP BY department;
```

| department | 人数 | 有奖金人数 | 平均奖金 | 统计年份 |
|---|---|---|---|---|
| 技术部 | 4 | 3 | 17666.67 | 2026 年 |
| 市场部 | 4 | 2 | 4000.00 | 2026 年 |
| 财务部 | 3 | 2 | 5000.00 | 2026 年 |
| 人事部 | 3 | 3 | 1833.33 | 2026 年 |

> 💡 **重点**：`COUNT(*)` 数组里有几行；`COUNT(bonus)` 只数 `bonus` 非 NULL 的行。技术部 4 人里王强的奖金是 NULL，所以「有奖金人数」是 **3**，平均奖金的分母也是 3（`53000 / 3 = 17666.67`）。**聚合函数跳过 NULL 的规则，分组后同样成立。**

> ❌ **常见错误**：想把每组的平均值再求个最大，写成 `MAX(AVG(salary))`：

```sql
SELECT MAX(AVG(salary)) FROM c2_employees GROUP BY department;
```

报错 `ERROR 1111 (HY000): Invalid use of group function`。`AVG` 已经把每组压成一个数字，`MAX` 没有「多行」可再压。真要「每组平均值的最大值」，得先分组算平均、再对结果做第二次查询（子查询，第 3 章）。

---

## 五、🔴 为什么不能 SELECT 未分组的列

**一句话点破：分组之后「行」被压成了「组」，组里 `name` 有 4 个不同的值，数据库不知道你要哪一个，只能拒绝。**

```sql
SELECT department, name, salary
FROM c2_employees
GROUP BY department;
```

**报错**：

```
ERROR 1055 (42000): Expression #2 of SELECT list is not in GROUP BY clause and contains
nonaggregated column 'learn.c2_employees.name' which is not functionally dependent on
columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by
```

翻成中文：`SELECT` 的第 2 个表达式 `name` 不在 `GROUP BY` 里，也没被聚合——违反 `ONLY_FULL_GROUP_BY`。

**为什么**：技术部那一组有 4 个人（张伟、李静、王强、赵敏）。你问「技术部的 `name` 是什么」，答案是 4 个，不是 1 个。

**一个类比**：把一箱苹果称出总重量，再问「这颗苹果多重」——总重量是整箱的，单颗的信息在称重那一刻就没了。`AVG(salary)` 一旦算出，组里每个人的工资就都「没了」。

### 那 MySQL 为什么「有时候」不报错？

因为 `ONLY_FULL_GROUP_BY` 可以关，老版本 MySQL（5.6 及更早）默认就是关的：

```sql
SET SESSION sql_mode = '';

SELECT department, name, salary
FROM c2_employees
GROUP BY department;
```

| department | name | salary |
|---|---|---|
| 技术部 | 张伟 | 28000.00 |
| 市场部 | 刘洋 | 12000.00 |
| 财务部 | 吴磊 | 10000.00 |
| 人事部 | 马超 | 7000.00 |

**不报错了，但它随便给了你一个人。** 张伟只是技术部里「碰巧先被读到」的那一行，换数据、换索引，可能就变成李静。

**这才是真正的坑**：技术部平均工资是 24500.00，张伟的 28000.00 既不是平均值，也不是最高值（最高是王强 30000.00）。你以为查到了「技术部代表员工」，其实只是随机抽签——今天张伟，删一行数据可能变成李静。

> ❌ **常见错误**：拿这种查询做报表。结果看起来「有模有样」，实际上 `name`、`salary` 和 `department` 的统计值根本对不上。**只要 SQL 里有 `GROUP BY` 又有没分组的普通列，就要警惕。**

```sql
-- 演示完记得恢复（只影响当前连接，不动全局配置）
SET SESSION sql_mode = DEFAULT;
```

> 💡 **重点**：MySQL 5.7 起默认开启 `ONLY_FULL_GROUP_BY`，报 1055 **是在保护你**。PostgreSQL、Oracle、SQL Server 也一律报错——这种写法在标准 SQL 里根本不存在。

### 那真的想要「随便取一个」怎么办？

把列加进 `GROUP BY` 能跑，但粒度变成「每个部门的每个人」，一个人一组、人数全是 1，通常不是你想要的；用 `MAX(salary)` 这种聚合函数，问的才是有唯一答案的问题。

确实只需要任意一个值，就用 `ANY_VALUE()` 明说：

```sql
SELECT department, ANY_VALUE(name) AS 任意员工,
       ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees
GROUP BY department;
```

返回 4 行：技术部张伟、市场部刘洋、财务部吴磊、人事部马超。`ANY_VALUE(name)` 的意思是「我知道 `name` 不唯一，我明确接受随便取一个」，MySQL 这才放行。

> ⚠️ **注意**：`ANY_VALUE()` 是 MySQL 提供的函数（别的数据库不一定有）；它只是让「随便取」变得**合法且显式**，并没有让这个值变得有意义。要「工资最高的那个人叫什么」，得用子查询或窗口函数（后面章节）。

---

## 六、GROUP BY 配合 ORDER BY：给统计结果排序

**一句话点破：统计结果也是结果，想按数值排就 `ORDER BY` 聚合结果——`ORDER BY` 在 `SELECT` 之后执行，所以能用别名。**

```sql
SELECT department, ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees
GROUP BY department
ORDER BY 平均工资 DESC;
```

| department | 平均工资 |
|---|---|
| 技术部 | 24500.00 |
| 市场部 | 11750.00 |
| 财务部 | 10333.33 |
| 人事部 | 7500.00 |

也可以直接排聚合表达式（`ORDER BY AVG(salary) DESC`），效果一样。多键排序就写 `ORDER BY 人数 DESC, 平均工资 DESC`，先按人数、再按平均工资。

> 💡 **重点**：`ORDER BY` 能用 `SELECT` 的别名，因为执行顺序是 `SELECT → ORDER BY`（第 1 章讲过）。**`GROUP BY` 不行**——它在 `SELECT` 之前。

> ⚠️ **注意**：**`GROUP BY` 自己不排序。** 前面几节看到「技术部、市场部、财务部、人事部」只是碰巧（MySQL 8.0 起取消了 `GROUP BY` 的隐式排序，5.7 及以前会按分组列偷偷排）。**需要顺序，就写 `ORDER BY`。**

> ❌ **常见错误**：在 `GROUP BY` 查询里按明细列排序：

```sql
SELECT department, ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees
GROUP BY department
ORDER BY salary DESC;
```

报 `ERROR 1055`：`ORDER BY` 里的 `salary` 不在 `GROUP BY` 里。分组后每组只剩一行，「每组的 `salary`」已经不存在了。要排就排聚合结果（`平均工资`）或分组列（`department`）。

---

## 七、GROUP BY 用表达式

**一句话点破：`GROUP BY` 后面不一定是列名，可以是表达式——数据库先算出每行表达式的值，再按这个值分堆。**

### 7.1 按入职年份分组

`hire_year` 是数字列，直接分组：

```sql
SELECT hire_year, COUNT(*) AS 人数, ROUND(AVG(salary), 0) AS 平均工资
FROM c2_employees
GROUP BY hire_year
ORDER BY hire_year;
```

7 行结果：2015 年 1 人 / 8000，2016 年 3 人 / 16500，2018 年 1 人 / 15000，2019 年 4 人 / 17500，2020 年 2 人 / 9000，2022 年 2 人 / 13500，2024 年 1 人 / 11000。分组列不必是文本，数字、日期都行——2019 年入职的 4 个人被分到同一堆。

### 7.2 按「年代」分档：真的用上表达式

需求变粗：五年一档。`DIV` 是整除：

```sql
SELECT hire_year DIV 5 * 5 AS 年代下限, COUNT(*) AS 人数,
       ROUND(AVG(salary), 2) AS 平均工资
FROM c2_employees
GROUP BY hire_year DIV 5 * 5
ORDER BY 年代下限;
```

结果两行：年代下限 2015 的 9 人 / 15833.33；年代下限 2020 的 5 人 / 11200.00。

`2019 DIV 5 * 5 = 2015`，`2024 DIV 5 * 5 = 2020`——每行先算出「年代下限」，再按这个值分成 2015-2019、2020-2024 两堆。

> ⚠️ **注意**：`SELECT` 里起了别名 `年代下限`，但 `GROUP BY` 里写的是**完整表达式**——这是可移植的写法（`GROUP BY` 用别名是 MySQL、PostgreSQL 的扩展，第八节讲）。

### 7.3 按工资区间分组

`CASE WHEN` 也是表达式，同样能拿来分组：

```sql
SELECT CASE WHEN salary < 10000 THEN '1 万以下'
            WHEN salary < 20000 THEN '1 万 - 2 万'
            ELSE '2 万以上' END AS 工资区间,
       COUNT(*) AS 人数, ROUND(AVG(salary), 2) AS 平均工资,
       MIN(salary) AS 最低, MAX(salary) AS 最高
FROM c2_employees
GROUP BY CASE WHEN salary < 10000 THEN '1 万以下'
              WHEN salary < 20000 THEN '1 万 - 2 万'
              ELSE '2 万以上' END
ORDER BY 最低;
```

| 工资区间 | 人数 | 平均工资 | 最低 | 最高 |
|---|---|---|---|---|
| 1 万以下 | 5 | 7900.00 | 6000.00 | 9500.00 |
| 1 万 - 2 万 | 6 | 13166.67 | 10000.00 | 18000.00 |
| 2 万以上 | 3 | 26666.67 | 22000.00 | 30000.00 |

先给每行贴一个区间标签，再按标签分三堆——和「按分数段把成绩单分成优秀、良好、及格三摞」是一个道理。按 5000 一档的简写是 `GROUP BY salary DIV 5000`（1 档 = 5000~9999，以此类推，本例 6 档）。

> 💡 **重点**：`SELECT` 和 `GROUP BY` 里的表达式必须**一致**，否则照样踩 1055：

```sql
-- ❌ 报错 1055
SELECT salary DIV 2000 AS 档位, COUNT(*) FROM c2_employees GROUP BY salary DIV 5000;
```

---

## 八、GROUP BY 的常见误解

### 误解 1：能按 SELECT 的别名分组，换数据库也可以

MySQL 里可以：

```sql
SELECT department AS 部门, COUNT(*) AS 人数
FROM c2_employees
GROUP BY 部门;
```

能跑（4 行）。PostgreSQL 也支持。但这是两个数据库**各自的扩展**——标准 SQL 规定 `GROUP BY` 引用输入列名，所以 Oracle、SQL Server 会报「列不存在」。

> 💡 **重点**：**`GROUP BY` 用别名不是标准 SQL。** 想写出可移植的 SQL，`GROUP BY` 里写真实列名；别名留给 `ORDER BY`（引用输出列名是标准允许的）。
>
> 一个类比：别名像小名——MySQL、PostgreSQL 这两家认小名，Oracle、SQL Server 和「标准 SQL」这家不认；去谁家办事，就按谁家的规矩报名。

### 误解 2：GROUP BY 会顺手把结果排好序

不会（至少不保证）。MySQL 8.0 起取消了 `GROUP BY` 的隐式排序；5.7 及以前会按分组列排，所以很多人**误以为**「`GROUP BY` 自带排序」。要顺序就写 `ORDER BY`。

### 误解 3：GROUP BY 后面只能写列名

错，表达式也可以（第七节）；甚至能写位置编号 `GROUP BY 1`——它指「按 `SELECT` 里第 1 个表达式分组」（这里就是 `department`），不是「按常量 1 分组」（那样全部 14 行会变成 1 组）。能跑，但可读性差、改 `SELECT` 顺序就变味，不推荐。

> ⚠️ **注意**：如果 `GROUP BY` 的列是表的**主键**（比如 `GROUP BY id`），MySQL 5.7+ 允许顺带选出这一行的其它列——主键能唯一确定一行（函数依赖）。**这不是「可以随便选未分组列」的许可**：按 `department` 分组时，`name` 照样报错。

---

## 本章小结

**完整写法**：

```sql
SELECT   分组列, 聚合函数(列)
FROM     表
WHERE    行筛选            -- 可选，分组之前
GROUP BY 分组列或表达式      -- 分堆
HAVING   组筛选            -- 下一篇
ORDER BY 排序键            -- 可排聚合结果
LIMIT    n;               -- 可选
```

**执行顺序**：`FROM → WHERE → GROUP BY（分堆）→ 聚合 → HAVING → SELECT → ORDER BY → LIMIT`

| 要点 | 说明 |
|---|---|
| 分堆 | 按列值分堆，**每堆一行结果** |
| 多列分组 | 按**组合**分堆，组数是真实出现过的组合数 |
| NULL | 所有 NULL 归成一组 |
| SELECT 限制 | 只能写**分组列 + 聚合函数 + 常量** |
| 未分组列 | 默认报 1055；关掉会随便给一个值（坑） |
| 表达式 | 先算表达式的值，再按值分堆 |
| 别名分组 | MySQL、PostgreSQL 行；标准 SQL 和 Oracle、SQL Server 不行 |

**三条铁律**：

1. **有 `GROUP BY`，`SELECT` 里就只放分组列和聚合函数**
2. **`GROUP BY` 不保证顺序，要顺序就写 `ORDER BY`**
3. **多列分组 = 组合键分组，别拿单列的组数去套**

---

## 动手练习

### 练习 1

统计每个部门的**人数**和**最高工资**。（答案见文末 **答案 1**）

### 练习 2

统计每个城市的**平均工资**（包括 `city` 为 NULL 的那组），按平均工资从高到低排。（答案见文末 **答案 2**）

### 练习 3

统计每个部门、每个城市的**人数**，按人数从多到少排，人数相同的按部门升序。（答案见文末 **答案 3**）

### 练习 4

按**入职年份**统计人数，按人数从多到少排，人数相同的按年份升序。（答案见文末 **答案 4**）

### 练习 5

把工资按**每 5000 一档**分组，统计每档人数和最高工资。（答案见文末 **答案 5**）

### 练习 6（陷阱题）

下面这条 SQL 能跑吗？如果不能，为什么？改成「每个部门最高工资」该怎么写？（答案见文末 **答案 6**）

```sql
SELECT department, name, MAX(salary) FROM c2_employees GROUP BY department;
```

---

## 下一篇

现在你会「分组统计」了，但还不会「只保留满足条件的组」——比如只要平均工资超过 1 万的部门。

**下一篇**：[03_HAVING过滤分组.md](03_HAVING过滤分组.md) —— `WHERE` 筛行，`HAVING` 筛组。

---

## 参考答案

> 先自己写，写完再对照。

### 答案 1

```sql
SELECT department, COUNT(*) AS 人数, MAX(salary) AS 最高工资 FROM c2_employees GROUP BY department;
```

技术部 4 / 30000.00；市场部 4 / 15000.00；财务部 3 / 13000.00；人事部 3 / 9500.00。

### 答案 2

```sql
SELECT city, ROUND(AVG(salary), 2) AS 平均工资 FROM c2_employees GROUP BY city ORDER BY 平均工资 DESC;
```

上海 17250.00、北京 15666.67、NULL 11000.00（周雨一个人）、广州 8166.67。NULL 也是一组。

### 答案 3

```sql
SELECT department, city, COUNT(*) AS 人数 FROM c2_employees
GROUP BY department, city ORDER BY 人数 DESC, department;
```

9 行。2 人的组合有 5 个：技术部北京、技术部上海、市场部北京、财务部上海、人事部广州；其余 4 个组合各 1 人。

### 答案 4

```sql
SELECT hire_year, COUNT(*) AS 人数 FROM c2_employees
GROUP BY hire_year ORDER BY 人数 DESC, hire_year;
```

2019 年 4 人（最多）；2016 年 3 人；2020、2022 年各 2 人；2015、2018、2024 年各 1 人。

### 答案 5

```sql
SELECT salary DIV 5000 AS 档位, COUNT(*) AS 人数, MAX(salary) AS 最高工资
FROM c2_employees GROUP BY salary DIV 5000 ORDER BY 档位;
```

1 档 5 人 / 9500.00；2 档 4 人 / 13000.00；3 档 2 人 / 18000.00；4、5、6 档各 1 人，最高工资分别 22000.00、28000.00、30000.00。

### 答案 6

**不能跑**，报 `ERROR 1055`：`name` 不在 `GROUP BY` 里，也没被聚合。

`MAX(salary)` 是「部门最高工资」，而 `name` 没有唯一答案（技术部 4 个人，到底取谁？）。MySQL 5.6 及更早、或关掉 `ONLY_FULL_GROUP_BY` 时它会随便给一个名字——那个名字和 `MAX(salary)` **没有任何关系**，只是组里碰巧被先读到的那个人，不要信。正确写法是只问「能唯一回答的问题」：

```sql
SELECT department, MAX(salary) AS 最高工资 FROM c2_employees GROUP BY department;
```

真要「最高工资的那个人是谁」，得用子查询或窗口函数（第 3 章、第 10 章）。如果只是给报表填个代表，用 `ANY_VALUE(name)`，但心里要清楚它没有业务含义。

