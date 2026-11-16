# 数据库学习环境说明

> 这份文档记录你的环境配置。**忘了密码、忘了怎么启动，回来查这里。**

---

## ⭐ 桌面上的 4 个图标

| 图标 | 名字 | 双击后 | 什么时候用 |
|---|---|---|---|
| 🐬 | **启动MySQL** | 启动数据库服务，显示连接信息 | **每次开机后**（MySQL 不会自启） |
| ⚙️ | **停止MySQL** | 关闭数据库服务 | 学完想关掉时（不关也行） |
| 💻 | **MySQL命令行** | 打开命令行，输密码 `Root@2026` 就能写 SQL | 想快速执行 SQL 时 |
| 🗄️ | **DB Browser for SQLite** | 打开图形界面，选 .db 文件查看 | **看数据最直观** |

**最常用的两个**：`启动MySQL`（开机第一件事）和 `DB Browser`（看数据）。

---

## 一、装了什么

| 工具 | 版本 | 用途 | 怎么打开 |
|---|---|---|---|
| **Python** | 3.15.2 | 写代码 | `python` |
| **sqlite3 模块** | SQLite 3.53.4 | 内置，零安装 | `import sqlite3` |
| **DB Browser for SQLite** | 3.13.1 | 图形界面看数据库 | 桌面图标 / 开始菜单 |
| **sqlite3 命令行** | 3.54.1 | 快速查数据 | `sqlite3 文件名.db` |
| **MySQL** | 26.10.0 | 服务器数据库 | 双击 `启动MySQL` |
| **PyMySQL** | 2.2.8 | Python 连 MySQL | `import pymysql` |
| **SQLite Viewer**（VS Code 扩展） | 26.9.1 | 在 VS Code 里看 .db | 双击 .db 文件 |

---

## 二、SQLite 怎么用

### 方式 1：Python 代码（学习主要用这个）

```python
import sqlite3

conn = sqlite3.connect("test.db")      # 文件不存在会自动创建
cur = conn.cursor()
cur.execute("CREATE TABLE t (id INTEGER, name TEXT)")
cur.execute("INSERT INTO t VALUES (?, ?)", (1, "小明"))
conn.commit()
cur.execute("SELECT * FROM t")
print(cur.fetchall())
conn.close()
```

### 方式 2：DB Browser（看数据最直观）

1. 双击桌面「**DB Browser for SQLite**」
2. 「打开数据库」→ 选 `.db` 文件
3. 三个常用标签页：
   - **数据库结构**：看有哪些表、字段类型
   - **浏览数据**：像 Excel 一样看表内容
   - **执行 SQL**：写 SQL 语句，`Ctrl+Enter` 执行

### 方式 3：命令行（快速查询）

```powershell
sqlite3 test.db

sqlite> .tables              # 看所有表
sqlite> .schema               # 看建表语句
sqlite> .headers on           # 显示列名
sqlite> .mode column          # 列对齐
sqlite> SELECT * FROM t;      # 查数据
sqlite> .quit                 # 退出
```

### 方式 4：VS Code 里直接看

在 VS Code 文件列表里**双击 `.db` 文件**，SQLite Viewer 会直接显示所有表和数据。

---

## 三、MySQL 怎么用

### 启动和停止（用桌面图标）

```
双击桌面「启动MySQL」  → 启动服务
双击桌面「停止MySQL」  → 关闭服务
```

**注意**：MySQL **不会开机自启**，每次电脑重启后要双击一次「启动MySQL」。

### 连接信息

```
地址：127.0.0.1
端口：3306
用户：root
密码：Root@2026
```

### 方式 1：桌面「MySQL命令行」

双击桌面「**MySQL命令行**」→ 输入密码 `Root@2026` → 直接写 SQL。

```sql
SHOW DATABASES;
CREATE DATABASE test;
USE test;
```

### 方式 2：命令行手动连

```powershell
mysql -u root -p
# 输入密码 Root@2026
```

### 方式 3：Python 连接

```python
import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="Root@2026",
    charset="utf8mb4"
)
cur = conn.cursor()
cur.execute("SELECT VERSION()")
print(cur.fetchone())
conn.close()
```

---

## 四、安全设置（已做好）

| 项 | 设置 | 说明 |
|---|---|---|
| 监听地址 | `127.0.0.1` | 只有本机能连，外部网络连不进来 |
| root 密码 | `Root@2026` | 已设置，不是空密码 |
| 字符集 | `utf8mb4` | 支持中文和 emoji |
| 慢查询日志 | 开启（>1 秒） | 学索引时能看哪些查询慢 |

---

## 五、常见问题

### Q1：MySQL 连不上

```
ERROR 2003: Can't connect to MySQL server
```

**解决**：双击桌面「**启动MySQL**」，等 10 秒再试。

### Q2：密码错误

```
ERROR 1045 (28000): Access denied
```

**解决**：密码是 `Root@2026`（大写 R、@ 符号、2026）。

### Q3：端口 3306 被占用

**解决**：先双击「**停止MySQL**」，再双击「**启动MySQL**」。

### Q4：DB Browser 打不开 .db 文件

**解决**：用 VS Code 的 SQLite Viewer 打开，或者 `sqlite3 文件名.db` 命令行查看。

### Q5：Python 报 `No module named 'pymysql'`

**解决**：
```powershell
python -m pip install pymysql
```

### Q6：中文变成乱码 / 问号

**解决**：
- Python 里加 `charset="utf8mb4"`
- 命令行里先执行 `chcp 65001`

---

## 六、验证脚本

不确定环境是否正常？运行这两个：

```powershell
cd "D:\deepseek工作区\学习\cs学习\自学库\数据库\_环境验证"
python 01_环境验证.py        # 检查 SQLite
python 02_MySQL验证.py       # 检查 MySQL
```

**两个都显示「全部就绪」= 可以开始学了。**

---

## 七、目录结构

```
数据库/
├── _环境验证/                  ← 环境检查（这个目录）
│   ├── 01_环境验证.py          ← SQLite 检查
│   ├── 02_MySQL验证.py         ← MySQL 检查
│   ├── 启动MySQL.bat           ← 桌面图标的实际脚本
│   ├── 停止MySQL.bat
│   └── README_环境说明.md       ← 你正在看的
├── 00_学前准备/                ← 从这里开始学
├── 01_查询基础/
├── 02_聚合分组/
├── 03_多表查询/
├── 04_增删改/
├── 05_建表约束/
├── 06_表设计/
├── 07_索引性能/
├── 08_事务/
├── 09_Python操作/
├── 10_进阶特性/
└── 11_实战项目/
```

---

## 八、学习路线（3 天速成版）

| 天 | 学什么 | 目标 |
|---|---|---|
| **第 1 天** | 00_学前准备 → 01_查询基础 | 会写 SELECT、WHERE、排序 |
| **第 2 天** | 02_聚合分组 → 03_多表查询 → 04_增删改 | 会统计、会联表、会改数据 |
| **第 3 天** | 09_Python操作 → 11_实战项目 | 能用 Python 建库做项目 |

**MySQL 的差异**放在遇到时再学（SQL 语法 95% 通用）。

---

## 九、文件存放位置

| 东西 | 位置 |
|---|---|
| 教程文件 | `D:\deepseek工作区\学习\cs学习\自学库\数据库\` |
| MySQL 数据 | `F:\Scoop\persist\mysql\data\` |
| MySQL 配置 | `F:\Scoop\persist\mysql\my.ini` |
| MySQL 慢查询日志 | `F:\Scoop\persist\mysql\slow.log` |
| 图标文件 | `F:\Scoop\icons\` |

**⚠️ 重要**：MySQL 数据在 `persist` 目录里，**升级/卸载 scoop 不会丢数据**。
但如果手动删了 `F:\Scoop\persist\mysql\data`，数据库就全没了。