# 第 10 章 · CTE 与视图

> 把长查询拆成读得懂的几步。每一步先写清楚，一行到底代表谁。

## 学习目标

- 用 WITH 把明细先汇总成订单，再筛选报表。
- 区分语句内使用的 CTE 和可复用的视图。

## 准备

复用第 05 章的电商数据。缺表时运行[第 05 章配套 SQL](../05_多表查询/00_安装配套表.sql)。本章报表计入游客的已付款订单，用明细成交价，统一口径先核对。
```sql
USE learn;
```

## 一、先算一笔订单，再过滤订单金额

不要在明细层用 `WHERE i.unit_price > 100` 近似「订单金额超过 100」。101 号由两条明细拼成 200 元，每条的单价都不超过 100。先统计到一单一行，再设门槛。

```sql
WITH paid_totals AS (
    SELECT o.id AS order_id, o.ordered_at,
           SUM(i.quantity * i.unit_price) AS total
    FROM c5_orders AS o
    JOIN c5_order_items AS i ON i.order_id = o.id
    WHERE o.status = 'paid'
    GROUP BY o.id, o.ordered_at
)
SELECT order_id, total
FROM paid_totals
WHERE total > 100.00
ORDER BY order_id;
```

| order_id | total |
|---:|---:|
| 101 | 200.00 |
| 103 | 120.00 |
| 105 | 210.00 |

`WITH` 中给中间结果一个名字，称为公共表表达式（CTE）。它在这条语句结束后失效。第 05 章的派生表也能表示这层结果，CTE 尤其适合把多个有先后依赖的步骤命名。CTE 并不保证生成物理临时表或更快，实际计划仍用 `EXPLAIN` 查看。

```sql
WITH paid_totals AS (
    SELECT o.id AS order_id, o.ordered_at,
           SUM(i.quantity * i.unit_price) AS total
    FROM c5_orders AS o
    JOIN c5_order_items AS i ON i.order_id = o.id
    WHERE o.status = 'paid'
    GROUP BY o.id, o.ordered_at
), large_orders AS (
    SELECT order_id, total FROM paid_totals WHERE total >= 100.00
)
SELECT COUNT(*) AS orders, SUM(total) AS revenue FROM large_orders;
```

仍是 3 笔，金额 530.00。输入是明细，第一层是一笔订单一行，第二层仍是一笔订单一行只是数量变少，最后输出整份清单的一行汇总。

## 二、再把可复用的查询定义存成视图

如果几个报表都需要同一套付款定义，可以用视图发布一份固定列结构。下面操作只创建本章的视图；先确认名称没有被自己以前的练习占用。演练最后清理该视图。多用户环境需要权限，本例用 `SQL SECURITY INVOKER`，查询时按调用者的权限检查。

```sql
CREATE SQL SECURITY INVOKER VIEW c10_paid_order_totals AS
SELECT o.id AS order_id, o.ordered_at,
       SUM(i.quantity * i.unit_price) AS total
FROM c5_orders AS o
JOIN c5_order_items AS i ON i.order_id = o.id
WHERE o.status = 'paid'
GROUP BY o.id, o.ordered_at;

SELECT order_id, total
FROM c10_paid_order_totals
ORDER BY order_id;

DROP VIEW c10_paid_order_totals;
```

查询看到 5 笔，金额依次 200、95、120、210、25。视图保存查询定义，查询时会基于当时的底表数据计算。删除视图只移除这个定义。聚合视图适合读取，不适合当作普通明细表写入。本课的任何写操作都无需改订单底表。

同一种报表如果以后需要「当时固定的留档数」，应保存带统计时间与口径的快照；视图会跟随付款状态和明细变化。

## 小结

临时拆分一条长查询用 CTE。大家都需要遵循同一个实时查询定义时，视图可以作为共同入口。

## 动手练习

### 练习 1 · 查看滤掉的那两单

在同一 CTE 上只找总额小于 100 的订单。

<details>
<summary>展开参考答案</summary>

```sql
WITH paid_totals AS (
    SELECT o.id AS order_id, o.ordered_at,
           SUM(i.quantity * i.unit_price) AS total
    FROM c5_orders AS o
    JOIN c5_order_items AS i ON i.order_id = o.id
    WHERE o.status = 'paid'
    GROUP BY o.id, o.ordered_at
)
SELECT order_id, total FROM paid_totals WHERE total < 100.00 ORDER BY order_id;
```

102 是 95.00，107 是 25.00。

</details>

### 练习 2 · 固定报表还是实时口径

财务需要留出 10 月结账时的报告供审计。直接只保存一个视图定义够吗？

<details>
<summary>展开参考答案</summary>

视图以后可能随底表状态改变。留档应保存带结账时间、统计口径和数据来源的结果快照。

</details>

**下一篇** [窗口函数与排名](02_窗口函数与排名.md)
