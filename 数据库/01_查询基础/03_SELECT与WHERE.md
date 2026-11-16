# 第 1 章 · WHERE 条件筛选

> 上一篇你学会了「选列」，但每次都拿到全部 5 行。**现实里你几乎不会要全部数据**——你要的是「分数超过 90 的」「一班的」「年龄大于 18 的」。
>
> `WHERE` 就是干这个的：**从一堆行里，只留下符合条件的。**

---

## 学习目标

1. 写出第一条 `WHERE` 条件
2. 掌握 6 个比较运算符
3. 用 `AND` `OR` `NOT` 组合条件（**注意优先级陷阱**）
4. 用 `IN` `BETWEEN` `LIKE` 做批量匹配
5. 正确处理 `NULL`（**最容易踩的坑**）

---

## 一、WHERE 的最基本用法

### 从「全都要」到「只要符合条件的」

**你现在会**：

```sql
SELECT name, score FROM students;
```

**5 行全出来。**

**现在想**：只要分数大于 90 的。

```sql
SELECT name, score FROM students
WHERE score > 90;
```

**结果**：

| name | score |
|---|---|
| 小明 | 92.50 |
| 小美 | 95.00 |

**只剩 2 行。**

---

### 语法结构

```sql
SELECT 列
FROM 表
WHERE 条件;
```

```
WHERE score > 90
       ↓     ↓  ↓
      列名  运算符 值
```

---

## 二、执行顺序（重要！）

### 你写的顺序 vs 实际执行的顺序

**你写的**：

```
SELECT → FROM → WHERE
```

**数据库实际执行的**：

```
FROM → WHERE → SELECT
```

### 这个区别意味着什么

**第 1 步：FROM** —— 先把 `students` 表的数据全拿出来

**第 2 步：WHERE** —— 再过滤掉不符合条件的行

**第 3 步：SELECT** —— 最后才挑选要显示哪些列

> 💡 **重点**：**WHERE 执行时，SELECT 还没执行。** 这解释了一个常见错误 ↓

---

### 常见错误：WHERE 里不能用 SELECT 的别名

**错误写法**：

```sql
SELECT name, score * 1.2 AS 加权分
FROM students
WHERE 加权分 > 100;    -- ❌ 报错
```

**报错**：

```
ERROR 1054 (42S22): Unknown column '加权分' in 'where clause'
```

**为什么**：`WHERE` 先执行，那时 `加权分` 这个别名还不存在。

**正确写法**：重复写完整表达式

```sql
SELECT name, score * 1.2 AS 加权分
FROM students
WHERE score * 1.2 > 100;   -- ✅
```

> ⚠️ **注意**：后面学 `ORDER BY` 时你会发现，**`ORDER BY` 里可以用别名**——因为它比 `SELECT` 后执行。

---

## 三、六个比较运算符

| 运算符 | 含义 | 例子 | 说明 |
|---|---|---|---|
| `=` | 等于 | `WHERE age = 18` | **一个等号**，不是 `==` |
| `!=` | 不等于 | `WHERE class != '一班'` | 也可以写 `<>` |
| `>` | 大于 | `WHERE score > 90` | |
| `<` | 小于 | `WHERE score < 80` | |
| `>=` | 大于等于 | `WHERE score >= 90` | |
| `<=` | 小于等于 | `WHERE score <= 80` | |

---

### 实战：每个运算符试一遍

**1. 等于**

```sql
SELECT name, age FROM students WHERE age = 18;
```

| name | age |
|---|---|
| 小明 | 18 |
| 小美 | 18 |

---

**2. 不等于**

```sql
SELECT name, class FROM students WHERE class != '一班';
```

| name | class |
|---|---|
| 小刚 | 二班 |
| 小美 | 二班 |

**也可以用 `<>`，效果一样**：

```sql
SELECT name, class FROM students WHERE class <> '一班';
```

---

**3. 大于**

```sql
SELECT name, score FROM students WHERE score > 90;
```

| name | score |
|---|---|
| 小明 | 92.50 |
| 小美 | 95.00 |

---

**4. 小于**

```sql
SELECT name, score FROM students WHERE score < 80;
```

| name | score |
|---|---|
| 小刚 | 76.50 |
| 小强 | 61.00 |

---

**5. 大于等于**

```sql
SELECT name, score FROM students WHERE score >= 88;
```

| name | score |
|---|---|
| 小明 | 92.50 |
| 小红 | 88.00 |
| 小美 | 95.00 |

**注意**：`>=` 和 `>` 的区别就是**要不要包含等于的那个**。88 分的小红出现了。

---

**6. 小于等于**

```sql
SELECT name, score FROM students WHERE score <= 76.5;
```

| name | score |
|---|---|
| 小刚 | 76.50 |
| 小强 | 61.00 |

---

## 四、字符串要用单引号

**这是新手最常犯的错误。**

### 正确写法

```sql
SELECT name FROM students WHERE class = '一班';
```

**单引号包起来。**

---

### 三种错误写法

**错误 1：不加引号**

```sql
SELECT name FROM students WHERE class = 一班;
```

**报错**：

```
ERROR 1054 (42S22): Unknown column '一班' in 'where clause'
```

**为什么**：`一班` 没引号，MySQL 以为是一个**列名**，找不到这列就报错。

---

**错误 2：用双引号**

```sql
SELECT name FROM students WHERE class = "一班";
```

**在 MySQL 里能跑**（MySQL 放宽了标准），**但不是标准 SQL**，换到 PostgreSQL 会报错。

---

**错误 3：用中文引号**

```sql
SELECT name FROM students WHERE class = ‘一班’;
```

**一定报错**。中文引号 `‘ ’` 不是 SQL 的引号。

> ⚠️ **注意**：写 SQL 时确保输入法是**英文状态**。中文引号长得像但完全不是一个字符。

---

## 五、AND：两个条件都要满足

**需求**：一班**并且**分数大于 80 的学生。

```sql
SELECT name, class, score
FROM students
WHERE class = '一班' AND score > 80;
```

**结果**：

| name | class | score |
|---|---|---|
| 小明 | 一班 | 92.50 |
| 小红 | 一班 | 88.00 |

**小强虽然是一班，但 61 分，不满足第二个条件，被排除。**

---

### 多个 AND

```sql
SELECT name, class, score
FROM students
WHERE class = '一班'
  AND score > 80
  AND age = 18;
```

**结果**：

| name | class | score |
|---|---|---|
| 小明 | 一班 | 92.50 |

**只有小明同时满足三个条件。**

---

## 六、OR：满足一个就行

**需求**：一班**或者**二班的学生（等于全部）。

```sql
SELECT name, class FROM students
WHERE class = '一班' OR class = '二班';
```

**更实用的例子**：分数大于 90 **或者** 小于 70 的（两头极端）。

```sql
SELECT name, score FROM students
WHERE score > 90 OR score < 70;
```

**结果**：

| name | score |
|---|---|
| 小明 | 92.50 |
| 小强 | 61.00 |
| 小美 | 95.00 |

---

## 七、🔴 AND / OR 的优先级陷阱（重点）

### 陷阱演示

**你想**：找出「一班或二班」里分数超过 85 的学生。

**直觉写法**：

```sql
SELECT name, class, score FROM students
WHERE class = '一班' OR class = '二班' AND score > 85;
```

**你以为的结果**：

| name | class | score |
|---|---|---|
| 小明 | 一班 | 92.50 |
| 小红 | 一班 | 88.00 |
| 小美 | 二班 | 95.00 |

**实际的结果**：

| name | class | score |
|---|---|---|
| 小明 | 一班 | 92.50 |
| 小红 | 一班 | 88.00 |
| 小强 | 一班 | 61.00 |
| 小美 | 二班 | 95.00 |

**4 行。多了一个小强（61 分）！**

---

### 为什么

**`AND` 的优先级高于 `OR`。** 所以数据库是这么理解的：

```sql
WHERE class = '一班'
   OR (class = '二班' AND score > 85)
   ↑ 这部分单独成立
```

**逐个判断**：

| name | class | score | 条件1<br>是一班？ | 条件2<br>二班且>85？ | OR 结果 |
|---|---|---|---|---|---|
| 小明 | 一班 | 92.5 | ✅ | ❌ | ✅ **留下** |
| 小红 | 一班 | 88.0 | ✅ | ❌ | ✅ **留下** |
| 小刚 | 二班 | 76.5 | ❌ | ❌（76.5<85） | ❌ 排除 |
| 小美 | 二班 | 95.0 | ❌ | ✅ | ✅ **留下** |
| 小强 | 一班 | 61.0 | ✅ | ❌ | ✅ **留下** |

**关键问题**：**小强 61 分也留下来了。**

你的本意是「分数超过 85」，但小强因为**是一班**，条件 1 成立，整个 `OR` 就成立了——**`score > 85` 根本没机会管他**。

---

### 正确写法：加括号

```sql
SELECT name, class, score FROM students
WHERE (class = '一班' OR class = '二班')
  AND score > 85;
```

**结果**：

| name | class | score |
|---|---|---|
| 小明 | 一班 | 92.50 |
| 小红 | 一班 | 88.00 |
| 小美 | 二班 | 95.00 |

**对了。**

---

### 铁律

> 💡 **重点**：**只要同时用 `AND` 和 `OR`，就用括号把 `OR` 的部分包起来。**

**记忆方法**：

```
AND 像乘法（优先级高）
OR  像加法（优先级低）

a OR b AND c   =  a OR (b AND c)
                 ≠  (a OR b) AND c
```

**和数学里 `1 + 2 × 3 = 7` 不是 `9` 一个道理。**

---

## 八、NOT：取反

```sql
SELECT name, class FROM students WHERE NOT class = '一班';
```

| name | class |
|---|---|
| 小刚 | 二班 |
| 小美 | 二班 |

**等价于**：

```sql
SELECT name, class FROM students WHERE class != '一班';
```

**用 `NOT` 的场景**：条件比较复杂时更清晰

```sql
-- 找出「不是一班也不是二班」的（本例里没有）
SELECT name, class FROM students
WHERE NOT (class = '一班' OR class = '二班');
```

---

## 九、IN：等于列表里任一个

### 问题：OR 写太多很啰嗦

```sql
SELECT * FROM students
WHERE class = '一班' OR class = '二班' OR class = '三班';
```

### 解决：用 IN

```sql
SELECT * FROM students WHERE class IN ('一班', '二班', '三班');
```

**一样的效果，但清爽多了。**

---

### 数字也能用 IN

```sql
SELECT name, id FROM students WHERE id IN (1, 3, 5);
```

| name | id |
|---|---|
| 小明 | 1 |
| 小刚 | 3 |
| 小强 | 5 |

---

### NOT IN：排除列表里的

```sql
SELECT name, class FROM students WHERE class NOT IN ('一班');
```

等于查二班的人。

---

## 十、BETWEEN：闭区间

### 语法

```sql
WHERE 列 BETWEEN 小值 AND 大值
```

### 例子：分数在 80 到 95 之间

```sql
SELECT name, score FROM students
WHERE score BETWEEN 80 AND 95;
```

**结果**：

| name | score |
|---|---|
| 小明 | 92.50 |
| 小红 | 88.00 |
| 小美 | 95.00 |

> 💡 **重点**：`BETWEEN` 是**闭区间**，包含 80 和 95 两个端点。
>
> 等价于 `score >= 80 AND score <= 95`。

---

### NOT BETWEEN：区间外

```sql
SELECT name, score FROM students
WHERE score NOT BETWEEN 80 AND 95;
```

| name | score |
|---|---|
| 小刚 | 76.50 |
| 小强 | 61.00 |

---

### 日期也能用 BETWEEN

```sql
SELECT * FROM students
WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31';
```

**查今年的数据。**

---

## 十一、LIKE：模糊匹配

### 两个通配符

| 通配符 | 含义 |
|---|---|
| `%` | 匹配**任意多个**字符（包括 0 个） |
| `_` | 匹配**恰好一个**字符 |

---

### 常见用法

**1. 以「小」开头**

```sql
SELECT name FROM students WHERE name LIKE '小%';
```

**结果**：全部 5 个人（都姓小）。

---

**2. 包含某个字**

```sql
SELECT name FROM students WHERE name LIKE '%明%';
```

| name |
|---|
| 小明 |

---

**3. 以某个字结尾**

```sql
SELECT name FROM students WHERE name LIKE '%强';
```

| name |
|---|
| 小强 |

---

**4. 恰好两个字的**

```sql
SELECT name FROM students WHERE name LIKE '__';
```

**两个下划线 = 恰好两个字符。**

---

**5. 第一个字随便，第二个字是「明」**

```sql
SELECT name FROM students WHERE name LIKE '_明';
```

---

### ⚠️ LIKE 的性能警告

```sql
-- 慢：% 开头，用不上索引，全表扫描
SELECT * FROM students WHERE name LIKE '%明%';

-- 快：不是 % 开头，能用索引
SELECT * FROM students WHERE name LIKE '小%';
```

**数据量大时，`%xxx%` 会非常慢。** 第 7 章讲索引时会细说。

---

## 十二、🔴 NULL 的特殊处理（最大的坑）

### 先说 NULL 是什么

```
0        → 确定的数字零
''       → 确定的空字符串
NULL     → 「没有值」/「不知道」
```

**NULL 不等于任何东西，包括它自己。**

---

### 陷阱 1：`= NULL` 查不到任何数据

**先造点数据**：

```sql
ALTER TABLE students ADD COLUMN phone VARCHAR(20);

UPDATE students SET phone = '13800000001' WHERE id = 1;
UPDATE students SET phone = '13800000002' WHERE id = 2;
```

**现在**：小明、小红有电话，其他三个是 NULL。

**错误写法**：

```sql
SELECT name, phone FROM students WHERE phone = NULL;
```

**结果**：**0 行！**

**为什么**：`NULL = NULL` 的结果是**「不知道」**，不是「真」。所以一行都匹配不上。

**正确写法**：

```sql
SELECT name, phone FROM students WHERE phone IS NULL;
```

| name | phone |
|---|---|
| 小刚 | NULL |
| 小美 | NULL |
| 小强 | NULL |

---

### 陷阱 2：`!= NULL` 也查不到

```sql
-- ❌ 0 行
SELECT name FROM students WHERE phone != NULL;
```

**正确**：

```sql
SELECT name, phone FROM students WHERE phone IS NOT NULL;
```

| name | phone |
|---|---|
| 小明 | 13800000001 |
| 小红 | 13800000002 |

---

### 陷阱 3：`NOT IN` 里放 NULL，永远查不到

```sql
-- ❌ 结果是空
SELECT * FROM students WHERE phone NOT IN ('13800000001', NULL);
```

**为什么**：`phone != NULL` 永远是「不知道」，所以整个条件都不成立。

> 💡 **重点**：**`NOT IN` 的列表里绝对不要放 NULL。**

---

### NULL 参与计算的结果

```sql
SELECT name, score + 10 AS 加分后 FROM students;
```

如果 `score` 是 NULL，结果**也是 NULL**（不是 10）。

**这个后面聚合函数会详细讲。**

---

## 十三、本章小结

### WHERE 支持的运算符

```
比较：  =  !=  <>  >  <  >=  <=
逻辑：  AND  OR  NOT
列表：  IN (...)  NOT IN (...)
区间：  BETWEEN 小 AND 大
模糊：  LIKE '模式'
空值：  IS NULL  IS NOT NULL
```

### 三条铁律

1. **`AND` 和 `OR` 混用必须加括号**
2. **字符串用单引号 `'text'`，不是双引号或中文引号**
3. **NULL 用 `IS NULL`，不能用 `= NULL`**

---

## 十四、动手练习

### 练习 1

查出分数在 80 到 90 之间的学生。

（答案见文末 **答案 1**）

---

### 练习 2

查出一班和二班的女生（假设名字带「小」的都是）。

**等等，这题没法判断性别。** 换个题：

查出**年龄 18 岁且分数大于 90** 的学生。

（答案见文末 **答案 2**）

---

### 练习 3

查出**没有登记电话**的学生。

（答案见文末 **答案 3**）

---

### 练习 4

查出名字**以「小」开头且第二个字不是「明」**的学生。

**提示**：需要组合 `LIKE` 和 `!=`。

（答案见文末 **答案 4**）

---

### 练习 5

查出一班里**分数低于 70 或高于 90** 的学生。

（答案见文末 **答案 5**）

---

### 练习 6（陷阱题）

下面这段代码想「查出分数不是 88 的学生」，能拿到几个结果？

```sql
SELECT name, score FROM students
WHERE score != 88;
```

再试试如果你给某个学生的 `score` 设成 NULL，会返回什么？

（答案见文末 **答案 6**）

---

## 十五、下一篇

现在你能「筛行」了，但结果顺序还是乱的。

**下一篇**：[04_排序与限制.md](04_排序与限制.md) —— 让结果按你的要求排，只取前 N 条。

---

## 附：WHERE 执行顺序图解

```
students 表（5 行）
    ↓
[FROM] 取出全部 5 行
    ↓
[WHERE] 过滤 → 只剩符合条件的
    ↓
[SELECT] 挑选要显示的列
    ↓
最终结果
```

**记住：WHERE 是「筛行」，SELECT 是「选列」。**


---

## 参考答案

> 先自己写，写完再对照。

### 答案 1

```sql
SELECT name, score FROM students
WHERE score BETWEEN 80 AND 90;
```

### 答案 2

```sql
SELECT name, age, score FROM students
WHERE age = 18 AND score > 90;
```

### 答案 3

```sql
SELECT name FROM students WHERE phone IS NULL;
```

### 答案 4

```sql
SELECT name FROM students
WHERE name LIKE '小%' AND name != '小明';
```

### 答案 5

```sql
SELECT name, class, score FROM students
WHERE class = '一班'
  AND (score < 70 OR score > 90);
```
**注意括号。** 去掉括号结果就错了。

### 答案 6

第一个问题：返回 4 行（小红 88 被排除）。

第二个问题：**NULL 的那个学生不会出现在结果里**！因为 `NULL != 88` 的结果是「不知道」，不是「真」。

**这和第 12 节讲的 NULL 陷阱是同一类问题。**
