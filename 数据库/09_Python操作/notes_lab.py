"""用相同的练习在 SQLite 和 MySQL 里读写笔记。"""
import argparse
from contextlib import closing
from getpass import getpass
from pathlib import Path
import sqlite3


def open_database(args):
    if args.engine == "sqlite":
        path = args.db.resolve()
        if args.command == "init":
            connection = sqlite3.connect(path, autocommit=False)
        else:
            connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, autocommit=False)
        return connection, "?"

    import pymysql

    connection = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user=args.mysql_user,
        password=getpass("本机 MySQL 密码: "),
        database="learn",
        charset="utf8mb4",
        autocommit=False,
        connect_timeout=5,
    )
    return connection, "%s"


def initialize_sqlite(connection):
    with closing(connection.cursor()) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS c9_notes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE CHECK (length(title) <= 100),
                minutes INTEGER NOT NULL CHECK (minutes BETWEEN 1 AND 600)
            ) STRICT
        """)
        cursor.executemany("""
            INSERT INTO c9_notes (title, minutes) VALUES (?, ?)
            ON CONFLICT(title) DO NOTHING
        """, [("单表查询", 20), ("多表查询", 35)])


def fetch_notes(connection, marker, min_minutes):
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            f"SELECT id, title, minutes FROM c9_notes WHERE minutes >= {marker} ORDER BY id",
            (min_minutes,),
        )
        return cursor.fetchall()


def insert_notes(connection, marker, entries):
    with closing(connection.cursor()) as cursor:
        cursor.executemany(
            f"INSERT INTO c9_notes (title, minutes) VALUES ({marker}, {marker})",
            entries,
        )
        return cursor.rowcount


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["sqlite", "mysql"], default="sqlite")
    parser.add_argument("--db", type=Path, default=Path("c9_notes.sqlite3"))
    parser.add_argument("--mysql-user", default="root")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="初始化 SQLite 练习文件")
    listing = commands.add_parser("list", help="按最低分钟数筛选")
    listing.add_argument("--min", type=int, default=1, dest="min_minutes")
    add = commands.add_parser("add", help="插入一条笔记")
    add.add_argument("title")
    add.add_argument("minutes", type=int)
    pair = commands.add_parser("add-pair", help="在同一事务中插入两条笔记")
    pair.add_argument("first_title")
    pair.add_argument("first_minutes", type=int)
    pair.add_argument("second_title")
    pair.add_argument("second_minutes", type=int)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.engine == "mysql" and args.command == "init":
        print("请先运行 00_安装配套表.sql，再用 list 或 add。")
        return 2

    if args.engine == "mysql":
        try:
            import pymysql
        except ImportError:
            print("当前 Python 未安装 PyMySQL。")
            return 2
        db_error = pymysql.MySQLError
    else:
        db_error = sqlite3.Error

    try:
        connection, marker = open_database(args)
    except db_error as error:
        print(f"连接失败：{error}")
        return 2

    with closing(connection):
        try:
            if args.command == "init":
                initialize_sqlite(connection)
                connection.commit()
                print(f"练习文件已就绪：{args.db}")
            elif args.command == "list":
                for id_, title, minutes in fetch_notes(connection, marker, args.min_minutes):
                    print(f"{id_} | {title} | {minutes} 分钟")
                connection.rollback()
            else:
                entries = (
                    [(args.title, args.minutes)] if args.command == "add"
                    else [(args.first_title, args.first_minutes),
                          (args.second_title, args.second_minutes)]
                )
                changed = insert_notes(connection, marker, entries)
                connection.commit()
                print(f"已提交 {changed} 条笔记。")
        except db_error as error:
            connection.rollback()
            print(f"操作失败，当前事务已撤回：{error}")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
