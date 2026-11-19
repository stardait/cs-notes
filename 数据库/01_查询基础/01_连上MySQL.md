# 第 01 章 · 连上 MySQL

> 先确认你连的是本机实例和 `learn`，再执行第一条查询。

## 学习目标

- 知道在 HeidiSQL 里在哪里开查询、哪里看结果。
- 用两条最简单的 SQL 验证服务器和当前库。
- 用错误提示区分连接、认证和表名问题。

## 准备

打开 HeidiSQL。新会话选 MySQL TCP/IP，主机 `127.0.0.1`，端口 `3306`，用户用本机已有账号，输入你自己的密码。服务没运行时，按[环境说明](../_环境验证/README_环境说明.md)启动。

## 操作

左侧是库和表，查询编辑区用于输入 SQL，结果格显示返回的行。按 `Ctrl+T` 开新查询标签。只粘当前代码块到编辑区，按 **F9** 执行整个编辑区；已有多个代码块时可选中当前一段按 **Ctrl+F9**，也可从执行按钮菜单选择运行选中部分。快捷键若自定义过，以 HeidiSQL 菜单显示为准。可查 [HeidiSQL 官方帮助](https://www.heidisql.com/help.php#running-sql-queries)。

```sql
SELECT 1 AS server_ok;
USE learn;
SELECT DATABASE() AS current_database;
SELECT COUNT(*) AS student_count FROM students;
```

正常时三个结果分别为 1、`learn`、5。第一条在没有默认库时也能运行。如果第一条成功而 `USE learn` 失败，连接已通，问题在当前账号可见的库。若 `learn` 或 `students` 在空环境中确实还没有，回看[首次初始化](../00_学前准备/01_数据库是什么.md)。

| 提示 | 先查什么 |
|---|---|
| `2003` 无法连上 | MySQL 是否已启动，主机与端口是否正确，3306 是否被其他服务占用 |
| `1045` 拒绝访问 | 用户名、密码和账号连接权限 |
| `1046` 未选默认库 | `USE learn` 或改用完整表名 |
| `1146` 表不存在 | 库名、表名和所在实例 |

## 小结

`SELECT 1` 检查能不能执行 SQL，`SELECT DATABASE()` 检查当前库，查 `students` 检查这节课的数据入口。

## 动手练习

### 练习 1 · 只查一次

证明当前连接能读到 `learn.students`。只返回学生编号、姓名。

<details>
<summary>展开参考答案</summary>

```sql
SELECT id, name FROM learn.students ORDER BY id;
```

当前样本应得到从小明到小强的 5 行。

</details>

**下一篇**：[第一条 SELECT](02_第一条SELECT.md)
