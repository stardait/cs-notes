# 第 05 章 · UNION 与写入查询结果

> 连接给记录加列，合并结果给清单加行。两边的列先对齐，再决定是否保留重复。

## 学习目标

- 用 UNION ALL 合并来源，按业务需求决定是否去重。
- 把验证正确的 SELECT 结果插入一张同结构语义的目标表。

## 准备

在 HeidiSQL 选择 `learn`。缺少 `c5_` 表时，先运行[本章配套 SQL](00_安装配套表.sql)。本章使用 5 名客户、7 笔订单、11 条明细、6 种商品，以及一张 3 人的员工表。订单状态为 `paid` 已付款、`pending` 待付款、`cancelled` 已取消。订单 107 是游客已付款订单，`customer_id` 为 `NULL`。
```sql
USE learn;
```

## 一、两段清单一列一列对齐

来自杭州和上海的客户，可能会重复进入不同筛选规则。先试一个有交集的例子。

```sql
SELECT id AS customer_id FROM c5_customers WHERE city = '杭州'
UNION ALL
SELECT id FROM c5_customers WHERE id <= 2
ORDER BY customer_id;

SELECT id AS customer_id FROM c5_customers WHERE city = '杭州'
UNION
SELECT id FROM c5_customers WHERE id <= 2
ORDER BY customer_id;
```

第一条是 1、1、2、3；第二条是 1、2、3。`UNION` 按整行去重。额外选来源标签时，同一个客户可能有不同标签，就成为两条不同记录。各段列数必须相同，对应列应表达同一类型含义，最终列名来自第一段。把全局 `ORDER BY` 写在最后。

```sql
SELECT id AS order_id, '网店订单' AS source FROM c5_orders WHERE id = 101
UNION ALL
SELECT 101, '手工登记'
ORDER BY source;
```

保留两个不同来源。只问计数或业务唯一项时，先明确按什么键去重。`UNION ALL` 省去合并阶段的去重语义；性能还需看各段查询的计划和数据量。内连接适合带回匹配值，`EXISTS` 适合判断是否存在，优先选择能正确表达目标粒度的写法。

## 二、同时保留没配上的客户和订单

MySQL 没有直接的 `FULL OUTER JOIN`。练习里的客户侧外连接有 7 行，已包含有匹配的记录和客户 5 的补空行。还缺没有客户的游客订单。用下面两个互斥的结果合并成一份清单。

```sql
SELECT c.id AS customer_id, o.id AS order_id
FROM c5_customers AS c
LEFT JOIN c5_orders AS o ON o.customer_id = c.id
UNION ALL
SELECT c.id, o.id
FROM c5_orders AS o
LEFT JOIN c5_customers AS c ON c.id = o.customer_id
WHERE c.id IS NULL
ORDER BY customer_id, order_id;
```

结果共 8 行。客户侧已经包括所有匹配，右侧分支只补未匹配订单，因此不会把匹配对抄两次。客户编号为空的游客 107 在排序里会排在前面。

## 三、选做：把已确认的结果保存下来

第 04 章使用 `VALUES` 明确给出数据。现在可以让一个查询返回所有待写行。这里创建仅当前会话可见的临时表，独立于订单表。临时表的下一条语句要在同一个 HeidiSQL 查询连接运行。演练末尾清理临时表。

```sql
CREATE TEMPORARY TABLE c5_paid_export (
    order_id INT PRIMARY KEY,
    customer_id INT
);

SELECT id, customer_id
FROM c5_orders
WHERE status = 'paid'
ORDER BY id;

INSERT INTO c5_paid_export (order_id, customer_id)
SELECT id, customer_id FROM c5_orders WHERE status = 'paid';

SELECT COUNT(*) AS exported_orders FROM c5_paid_export;
DROP TEMPORARY TABLE c5_paid_export;
```

先预览 101、102、103、105、107，再确认目标列的位置与来源一致。复制 5 行，游客的客户号仍为 `NULL`。目标表的主键约束也照常执行。把同一批直接重复写入会发生主键冲突，保存历史导出时应先约定覆盖、跳过或生成新批次。

## 小结

合并清单先对齐列、再定重复的含义。复制查询结果时，先单跑来源查询核对编号和数量。

## 动手练习

### 练习 1 · 留住客户来源标签

把杭州客户与编号不超过 2 的客户合成一份带来源的清单，是否应有两条客户 1？

<details>
<summary>展开参考答案</summary>

```sql
SELECT id AS customer_id, '来自杭州' AS reason FROM c5_customers WHERE city = '杭州'
UNION ALL
SELECT id, '编号不超过 2' FROM c5_customers WHERE id <= 2
ORDER BY customer_id, reason;
```

应有两条，含义是客户 1 同时满足两条规则。

</details>

### 练习 2 · 备份待付款的表头记录

写入前先预览待付款订单号。临时表只保存订单号，应插入哪些行？

<details>
<summary>展开参考答案</summary>

```sql
SELECT id FROM c5_orders WHERE status = 'pending' ORDER BY id;
```

只有 104。若按本课方式建立一列临时目标表，写入时对应的 SELECT 只返回 id 一列。

</details>

**下一篇** [多表查询综合练习](06_综合练习.md)
