"""
================================================================================
环境验证脚本 —— MySQL 部分
================================================================================
用途：确认 Python 能连上你的 MySQL。

运行：python 02_MySQL验证.py
================================================================================
"""

import sys

# ---------- 配置（如果要改密码，改这里） ----------
MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Root@2026",
    "charset": "utf8mb4",
}


def check(title, fn):
    print(f"  {title:<34}", end="")
    try:
        print(f"✅ {fn()}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


print()
print("=" * 70)
print("MySQL 环境验证")
print("=" * 70)
print()


# ---------- 1. 驱动 ----------
print("【1】Python 驱动")


def check_driver():
    import pymysql
    return f"PyMySQL {pymysql.__version__}"


results = [check("PyMySQL 已安装", check_driver)]
print()


# ---------- 2. 连接测试 ----------
print("【2】连接 MySQL")


def test_connect():
    import pymysql
    conn = pymysql.connect(**MYSQL_CONFIG)
    conn.close()
    return f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}"


results.append(check("能连上服务器", test_connect))


def test_version():
    import pymysql
    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT VERSION()")
    v = cur.fetchone()[0]
    conn.close()
    return f"MySQL {v}"


results.append(check("查询版本", test_version))


def test_charset():
    import pymysql
    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute("SHOW VARIABLES LIKE 'character_set_server'")
    row = cur.fetchone()
    conn.close()
    return f"{row[1]}"


results.append(check("服务器字符集", test_charset))
print()


# ---------- 3. 建库建表测试 ----------
print("【3】实际操作测试")

TEST_DB = "env_test"


def test_create_db():
    import pymysql
    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    conn.close()
    return TEST_DB


results.append(check("创建数据库", test_create_db))


def test_create_table():
    import pymysql
    cfg = dict(MYSQL_CONFIG, database=TEST_DB)
    conn = pymysql.connect(**cfg)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS demo")
    cur.execute("""
        CREATE TABLE demo (
            id   INT PRIMARY KEY AUTO_INCREMENT,
            msg  VARCHAR(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    conn.close()
    return "demo 表"


results.append(check("创建表", test_create_table))


def test_insert():
    import pymysql
    cfg = dict(MYSQL_CONFIG, database=TEST_DB)
    conn = pymysql.connect(**cfg)
    cur = conn.cursor()
    cur.execute("INSERT INTO demo (msg) VALUES (%s)", ("你好，MySQL！",))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return f"插入 id={new_id}"


results.append(check("插入中文数据", test_insert))


def test_select():
    import pymysql
    cfg = dict(MYSQL_CONFIG, database=TEST_DB)
    conn = pymysql.connect(**cfg)
    cur = conn.cursor()
    cur.execute("SELECT id, msg FROM demo")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        raise ValueError("没有查到数据")
    return rows[-1][1]


results.append(check("查询中文数据", test_select))


def test_cleanup():
    import pymysql
    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
    conn.commit()
    conn.close()
    return "已清理测试库"


results.append(check("清理测试数据", test_cleanup))
print()


# ---------- 汇总 ----------
print("=" * 70)
passed = sum(1 for r in results if r)
print(f"自动化检查：{passed}/{len(results)} 通过")
print("=" * 70)
print()

if passed == len(results):
    print("🎉 MySQL 环境全部就绪！")
else:
    print("⚠️  有检查未通过，常见原因：")
    print("    · MySQL 服务没启动 → 运行「启动MySQL.bat」")
    print("    · 密码不对 → 改本文件顶部的 MYSQL_CONFIG")

print()
