"""SQLite 学习记录工具。所有命令在自己选定的练习文件上执行。"""
import argparse
from contextlib import closing
from datetime import date
from pathlib import Path
import sqlite3


SCHEMA = Path(__file__).with_name("00_SQLite建表.sql")
REPORT_SQL = """
SELECT t.name, COUNT(s.id) AS session_count, COALESCE(SUM(s.minutes), 0) AS total_minutes
FROM c11_topics AS t
LEFT JOIN c11_sessions AS s ON s.topic_id = t.id
  AND s.studied_on >= ? AND s.studied_on < ?
GROUP BY t.id, t.name
ORDER BY total_minutes DESC, t.id
"""
INSERT_SESSION_SQL = """
    INSERT INTO c11_sessions (topic_id, studied_on, minutes, note)
    SELECT id, ?, ?, ?
    FROM c11_topics
    WHERE name = ? AND archived = 0
"""


def iso_day(value):
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("日期格式必须是 YYYY-MM-DD。") from error
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("日期格式必须是 YYYY-MM-DD。")
    return value


def open_database(path, create=False):
    path = path.resolve()
    if create:
        connection = sqlite3.connect(path, autocommit=True)
    else:
        connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, autocommit=True)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def add_session(connection, topic, studied_on, minutes, note):
    cursor = connection.execute(INSERT_SESSION_SQL, (studied_on, minutes, note, topic))
    if cursor.rowcount != 1:
        raise ValueError("找不到该主题，或主题已归档。")


def seed_demo(connection):
    if connection.execute("SELECT 1 FROM c11_topics LIMIT 1").fetchone():
        raise ValueError("演示数据只写入没有主题的新文件。")
    connection.executemany("INSERT INTO c11_topics (name) VALUES (?)",
                           [("SQL",), ("Python",), ("分析",)])
    for row in [
        ("SQL", "2026-11-01", 25, "SELECT"),
        ("SQL", "2026-11-12", 35, "JOIN"),
        ("Python", "2026-11-08", 30, "sqlite3"),
        ("SQL", "2026-12-01", 45, "索引"),
    ]:
        add_session(connection, *row)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("c11_study.sqlite3"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="创建练习数据库及表")
    sub.add_parser("demo", help="给空练习库加入样本数据")
    topic = sub.add_parser("topic", help="创建主题")
    topic.add_argument("name")
    archive = sub.add_parser("archive", help="归档主题，保留历史")
    archive.add_argument("name")
    session = sub.add_parser("session", help="记录一次学习")
    session.add_argument("topic")
    session.add_argument("studied_on", type=iso_day)
    session.add_argument("minutes", type=int)
    session.add_argument("--note", default="")
    report = sub.add_parser("report", help="统计一个左闭右开的日期区间")
    report.add_argument("start", type=iso_day)
    report.add_argument("end", type=iso_day)
    args = parser.parse_args(argv)
    if args.command == "report" and args.start >= args.end:
        parser.error("起始日期必须早于截止日期。")
    return args


def run_command(connection, args):
    if args.command == "report":
        rows = connection.execute(REPORT_SQL, (args.start, args.end)).fetchall()
        for name, count, minutes in rows:
            print(f"{name} | {count} 次 | {minutes} 分钟")
        return

    if args.command == "demo":
        seed_demo(connection)
        message = "已提交 3 个主题和 4 条演示记录。"
    elif args.command == "topic":
        connection.execute("INSERT INTO c11_topics (name) VALUES (?)", (args.name.strip(),))
        message = "主题已创建。"
    elif args.command == "session":
        add_session(connection, args.topic.strip(), args.studied_on, args.minutes, args.note)
        message = "学习记录已保存。"
    else:
        cursor = connection.execute(
            "UPDATE c11_topics SET archived = 1 WHERE name = ? AND archived = 0",
            (args.name.strip(),),
        )
        if cursor.rowcount != 1:
            raise ValueError("找不到该主题，或主题已归档。")
        message = "主题已归档，历史记录保留。"
    return message


def main(argv=None):
    args = parse_args(argv)
    try:
        with closing(open_database(args.db, create=args.command == "init")) as connection:
            if args.command == "init":
                connection.executescript(SCHEMA.read_text(encoding="utf-8"))
                print(f"数据库已就绪：{args.db}")
                return 0

            connection.autocommit = False
            with connection:
                message = run_command(connection, args)
            if message:
                print(message)
    except (sqlite3.Error, ValueError, OSError) as error:
        print(f"操作失败：{error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
