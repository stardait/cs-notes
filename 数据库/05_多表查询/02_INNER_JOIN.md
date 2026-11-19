# 第 05 章 · INNER JOIN

> 先确定两行在什么条件下能配成一行，再看一个编号会配出几行。

## 学习目标

- 写出连接条件和表别名，预测内连接留下的行。
- 识别一对多连接造成的行数变化，并用正确单位计数。

## 准备

在 HeidiSQL 选择 `learn`。缺少 `c5_` 表时，先运行[本章配套 SQL](00_安装配套表.sql)。本章使用 5 名客户、7 笔订单、11 条明细、6 种商品，以及一张 3 人的员工表。订单状态为 `paid` 已付款、`pending` 待付款、`cancelled` 已取消。订单 107 是游客已付款订单，`customer_id` 为 `NULL`。
```sql
USE learn;
```

## 一、先把订单和客户配对

```sql
SELECT o.id AS order_id, c.name, o.status
FROM c5_orders AS o
INNER JOIN c5_customers AS c ON c.id = o.customer_id
ORDER BY o.id;
```

结果是 101～106 共 6 行。订单 107 的客户号为空，找不到匹配。客户 5 没有订单，也不出现在结果中。`o` 和 `c` 是表别名。两张表都有 `id`，使用 `o.id` 和 `c.id` 可以说清引用哪一张表，输出名再用 `AS order_id` 标记。

要手算逻辑，可以先想象每笔订单和每个客户组成候选对。下面的无条件 `CROSS JOIN` 实际返回 `7×5=35` 对的计数。加编号条件后，有效匹配是 6 对。这个计数帮助理解匹配规则，数据库的实际访问路径由优化器选择。

```sql
SELECT COUNT(*) AS candidate_pairs
FROM c5_orders AS o CROSS JOIN c5_customers AS c;
```

旧代码有时用逗号列两张表，再把编号相等写进 `WHERE`。内连接可表达相同逻辑，显式写 `JOIN … ON` 会把关联键和状态等业务条件放到容易辨认的位置。只需要所有组合时，才有意使用 `CROSS JOIN`，例如两家仓库和三天组成六个检查时段。

## 二、接进明细和商品后，一笔订单会变成多行

```sql
SELECT o.id AS order_id, i.line_no, p.name, i.quantity, i.unit_price
FROM c5_orders AS o
INNER JOIN c5_order_items AS i ON i.order_id = o.id
INNER JOIN c5_products AS p ON p.id = i.product_id
WHERE o.id IN (101, 105)
ORDER BY o.id, i.line_no;
```

| order_id | line_no | name | quantity | unit_price |
|---:|---:|---|---:|---:|
| 101 | 1 | 键盘 | 1 | 100.00 |
| 101 | 2 | 鼠标 | 2 | 50.00 |
| 105 | 1 | 键盘 | 1 | 105.00 |
| 105 | 2 | 咖啡豆 | 1 | 65.00 |
| 105 | 3 | 茶包 | 2 | 20.00 |

连到明细表后，一行变成一个订单里的一个明细位置。商品内连接还保持 5 行，因为每条明细有且只有一个真实商品编号。这不是重复错误。把 `DISTINCT` 加到所有查询上可能把两条确实不同的记录合并掉。

```sql
SELECT COUNT(*) AS line_count, COUNT(DISTINCT o.id) AS orders
FROM c5_orders AS o
INNER JOIN c5_order_items AS i ON i.order_id = o.id
WHERE o.status = 'paid';
```

结果是 9 条明细、5 笔订单。这里没有连接客户表，游客订单仍参与。用金额字段求和时，先查是否又接入了另一张一对多表，比如售后事件，防止一条明细被多个匹配多次计入。

官方语法可查 [MySQL JOIN](https://dev.mysql.com/doc/refman/26.10/en/join.html)。

## 小结

从一行的粒度、关联键和无匹配时的结果三件事开始写连接。先用明细结果验证，再考虑计数。

## 动手练习

### 练习 1 · 选中重复行的原因

只查 101 号订单及其明细序号。为什么不只返回 1 行？

<details>
<summary>展开参考答案</summary>

```sql
SELECT o.id, i.line_no
FROM c5_orders AS o JOIN c5_order_items AS i ON i.order_id = o.id
WHERE o.id = 101 ORDER BY i.line_no;
```

它的两个明细分别与同一订单匹配，行号 1、2 都会出现。

</details>

### 练习 2 · 客户内连接后的已付款数

给明细计数示例再接上客户表，用相同口径查订单数和明细数。

<details>
<summary>展开参考答案</summary>

```sql
SELECT COUNT(DISTINCT o.id) AS orders, COUNT(*) AS line_count
FROM c5_orders AS o
JOIN c5_order_items AS i ON i.order_id = o.id
JOIN c5_customers AS c ON c.id = o.customer_id
WHERE o.status = 'paid';
```

4 笔、8 条；游客 107 没有客户记录，连同它的一条明细被排除。

</details>

**下一篇** [外连接与自连接](03_外连接与自连接.md)
