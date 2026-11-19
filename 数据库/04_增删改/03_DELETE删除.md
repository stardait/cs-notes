# 第 04 章 · DELETE 删除

> 删除前要认得出每一条目标记录，删除后要有办法验证它们确实该消失。

## 学习目标

- 用条件和确定性顺序删除记录，区分物理删除与软删除。
- 用实验区分 `DELETE`、`TRUNCATE TABLE` 和 `DROP TABLE`。
- 区分尚未提交的误删与提交后的恢复，并在练习表里做一次恢复。

## 准备

`c4c_employees` 初始有 9 行。演示表 `c4c_delete_lab` 在最后一节创建。看到预期错误的代码块时单独执行。写入实验使用相同查询标签，最后执行回滚或清理。

```sql
USE learn;
SELECT id, employee_no, name, status, hired_on
FROM c4c_employees ORDER BY id;
```

## 一、按条件删除行

员工 5 已离职，现在模拟按编号清理其档案。先查编号、工号和状态，带着同样的条件去删。

```sql
START TRANSACTION;
SELECT id, employee_no, status FROM c4c_employees WHERE id = 5 AND status = 'left';
DELETE FROM c4c_employees WHERE id = 5 AND status = 'left';
SELECT ROW_COUNT() AS deleted;
SELECT COUNT(*) AS still_present FROM c4c_employees WHERE id = 5;
ROLLBACK;
```

预览应是 `5, E005, left`。删除后影响 1 行，再查存在数是 0。查询之所以还能执行，是因为表结构依旧在。`DELETE FROM` 之后直接写表名。与 `SELECT` 不同，删除时不写要取的列。

## 二、漏写 WHERE 的恢复实验

下面特意删去条件来观察后果。只在 `c4c_employees` 的显式事务里运行整段。若开启安全更新而收到 `1175`，执行 `ROLLBACK;` 后继续学习。

```sql
START TRANSACTION;
SELECT COUNT(*) AS rows_before FROM c4c_employees;
DELETE FROM c4c_employees;
SELECT COUNT(*) AS rows_after FROM c4c_employees;
ROLLBACK;
SELECT COUNT(*) AS rows_restored FROM c4c_employees;
```

按顺序看到 9、0、9。事务中可以在提交前撤回。若在自动提交模式下漏了 `START TRANSACTION`，删除会立即提交。回滚不能撤销已经提交的删除。

## 三、三种表操作怎么选

下表以普通 InnoDB 表为前提。

| 操作 | 动了什么 | 能带 `WHERE` | 显式事务可回滚 | 表结构 | 自增编号 |
|---|---|---|---|---|---|
| `DELETE FROM` | 符合条件的行；省去条件就是全部行 | 可以 | 可以，在提交前 | 保留 | 一般不会重置 |
| `TRUNCATE TABLE` | 整表内容 | 不行 | 不可，属于隐式提交的 DDL | 逻辑结构保留 | 重置 |
| `DROP TABLE` | 表和全部数据 | 不行 | 不可，普通表属于隐式提交的 DDL | 删除 | 表已经不存在 |

清理全部数据时 `TRUNCATE` 通常比逐行 `DELETE` 快，实际要考虑存储引擎、约束和持锁。在 InnoDB，存在其他表引用时，`TRUNCATE` 还可能被外键阻止。选命令时先问你要删一批记录、清空整表还是移除表本身。

用新建的练习表比较编号。这个普通表只做实验，不承载正文练习数据。

```sql
CREATE TABLE c4c_delete_lab (
    id INT PRIMARY KEY AUTO_INCREMENT,
    label VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

INSERT INTO c4c_delete_lab (label) VALUES ('甲'), ('乙');
DELETE FROM c4c_delete_lab WHERE id IN (1, 2);
INSERT INTO c4c_delete_lab (label) VALUES ('丙');
SELECT id, label FROM c4c_delete_lab;

TRUNCATE TABLE c4c_delete_lab;
INSERT INTO c4c_delete_lab (label) VALUES ('丁');
SELECT id, label FROM c4c_delete_lab;
```

默认自增步长下，两次分别为 `3, 丙` 和 `1, 丁`。`TRUNCATE` 会隐式提交。操作其他数据的事务里也应避免夹进这条命令。

## 四、按序分批删，或保留历史

把离职记录按入职日排序，日期相同时按主键。先试删最早的一条。预览时两处排序和限制保持一致。

```sql
START TRANSACTION;
SELECT id, hired_on FROM c4c_employees
WHERE status = 'left' ORDER BY hired_on, id LIMIT 1;
DELETE FROM c4c_employees
WHERE status = 'left' ORDER BY hired_on, id LIMIT 1;
SELECT ROW_COUNT() AS deleted;
SELECT id FROM c4c_employees WHERE status = 'left' ORDER BY hired_on, id;
ROLLBACK;
```

预览 `id=7`，影响 1 行，剩下离职的 5、6。`LIMIT` 限的是这一批行数。下一批会在新的表状态下再次筛目标，仍要检查条件与可重现顺序。

如果业务要求保留档案但从日常结果隐藏，用 `deleted_at` 标记。例如以下操作保留了 5 号员工行。离职 `status='left'` 是业务状态，软删除标记是可见性，两件事可同时存在。

```sql
START TRANSACTION;
SELECT id, status, deleted_at FROM c4c_employees WHERE id = 5;
UPDATE c4c_employees SET deleted_at = CURRENT_TIMESTAMP
WHERE id = 5 AND status = 'left' AND deleted_at IS NULL;
SELECT ROW_COUNT() AS archived;
SELECT id, deleted_at IS NOT NULL AS is_archived FROM c4c_employees WHERE id = 5;
SELECT id FROM c4c_employees WHERE id = 5 AND deleted_at IS NULL;
ROLLBACK;
```

影响 1 行，普通查询仍看到 `(5, 1)`，带 `deleted_at IS NULL` 的查询返回零行。软删后主键和唯一工号依然被占用。什么时候物理清理、哪些报表包含历史，都要由业务规则给定。

## 五、已提交误删怎么恢复

在继续使用 `c4c_delete_lab` 之前，先检查当前行。预期有一行 `(1, '丁')`。把这两列作为本练习的完整备份，提前存到独立的 SQL 文本，内容是后面显示的那条恢复语句。源表若还有其他列，也要一并保存。下一篇会完整练习导出。

```sql
SELECT id, label FROM c4c_delete_lab WHERE id = 1;
START TRANSACTION;
DELETE FROM c4c_delete_lab WHERE id = 1;
COMMIT;
ROLLBACK;
SELECT COUNT(*) AS still_missing FROM c4c_delete_lab WHERE id = 1;
```

存在数仍是 0。现在确认原主键空着，再把之前保存的行插回。实际恢复前也要查其他唯一键有没有冲突，先在隔离环境验收。

```sql
INSERT INTO c4c_delete_lab (id, label) VALUES (1, '丁');
SELECT id, label FROM c4c_delete_lab WHERE id = 1;
DROP TABLE c4c_delete_lab;
SHOW TABLES LIKE 'c4c_delete_lab';
```

先重新得到 `1, 丁`，最后的查表结果为零行。误删后的新写入需要保留，恢复范围应与实际受损的行相符。

## 小结

`DELETE` 针对行。需要保留历史时，先设计状态和可见性。提前存好可用的副本，遇到已提交误删才有可靠恢复来源。

## 动手练习

### 练习 1 · 年界线

找并删除 2023 年以前入职、且已经离职的人。2023-01-01 入职不满足。验证后回滚。

<details>
<summary>展开参考答案</summary>

```sql
START TRANSACTION;
SELECT id, hired_on FROM c4c_employees
WHERE status = 'left' AND hired_on < '2023-01-01' ORDER BY id;
DELETE FROM c4c_employees WHERE status = 'left' AND hired_on < '2023-01-01';
SELECT ROW_COUNT() AS deleted;
SELECT id, status FROM c4c_employees WHERE id IN (5, 6, 7) ORDER BY id;
ROLLBACK;
```

删除 5、7，共 2 行。`id=6` 正好卡在边界，保留。

</details>

### 练习 2 · 选择清理手段

临时导入表的全部行已作废，表结构会给下一批继续用，编号要从头计数。用什么命令？什么时候应该换方案？

<details>
<summary>展开参考答案</summary>

表可安全清空且允许隐式提交时，可以用 `TRUNCATE TABLE`。若要用事务在提交前检查、回滚，或只删除某一批记录，选 `DELETE` 并给出目标条件。

</details>

### 练习 3 · 离职和软删除

报表要显示所有未归档的离职人员。应该写哪两个条件，现有练习表返回哪些编号？

<details>
<summary>展开参考答案</summary>

```sql
SELECT id FROM c4c_employees
WHERE status = 'left' AND deleted_at IS NULL ORDER BY id;
```

回滚前面的演示后，返回 5、6、7。`status` 回答是否在职，`deleted_at` 回答当前是否归档。

</details>

**下一篇**：[安全操作习惯](04_安全操作习惯.md)
