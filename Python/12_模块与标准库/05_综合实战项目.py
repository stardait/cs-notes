"""
================================================================================
第 12 章 · 模块与标准库
文件 05：综合实战项目 —— 命令行待办事项管理器
================================================================================

【学习目标】
    1. 把前 4 个文件的知识（模块、json、os、argparse）串成一个真项目
    2. 学会「分层设计」：存储层 / 业务层 / 界面层各管一件事
    3. 掌握 JSON 文件持久化（含原子写入，防数据损坏）
    4. 用 argparse 做一个真正的命令行工具

【怎么用这个文件】
    - 不带参数运行（python 05_综合实战项目.py）→ 跑完整演示，用临时文件、
      跑完自动删除，不污染当前目录
    - 带参数运行 → 演示跑完后，再执行你的命令（会生成数据文件）：
        python 05_综合实战项目.py --data my.json add "买牛奶" -p 1
        python 05_综合实战项目.py --data my.json list
    【说明】演示写在模块顶层（为了「从上往下读就有输出」），所以它总会先跑；
      真实项目会把演示挪进 main() 分支，那样带参数时就只剩命令本身。

【前置知识】
    - 本文件 01~04（模块、json、os、try/except、依赖注入都会用到）
================================================================================
"""

import argparse                     # 命令行参数解析
import json                         # 数据持久化
import os                           # 路径与文件操作
import sys                          # argv、解释器路径
import tempfile                     # 演示用的临时目录
import shutil                       # 删除临时目录
from datetime import datetime       # 记录创建时间


# ==============================================================================
# 知识点 1：项目设计 —— 先分层，再写代码
# ==============================================================================
#
# 【讲解】写项目最忌讳「一个文件从头 if 到尾」。专业做法是分成三层：
#   存储层 Storage 管「数据怎么存到硬盘、怎么读回来」；业务层 TodoManager 管
#   「增删改查和统计规则」；界面层 main / argparse 管「接收命令、打印结果」。
# 【重点】分层的好处：换存储（JSON 换数据库）只改 Storage；换界面（命令行换网页）
#   只改界面层；写测试只测 TodoManager。就像餐厅的「后厨」「仓库」「服务员」，
#   服务员换人了后厨不用动；每一层只依赖「下一层的接口」，这叫「面向接口编程」。

print("--- 项目设计：三层结构 ---")
print(f"{'Storage 存储层':<20} 负责「数据怎么落盘」，主要用：json.dump / json.load / os.replace")
print(f"{'TodoManager 业务层':<20} 负责「规则怎么算」，主要用：add / list / done / remove / stats")
print(f"{'main 界面层':<20} 负责「命令怎么接」，主要用：argparse + print")

# 输出：
# --- 项目设计：三层结构 ---
# Storage 存储层          负责「数据怎么落盘」，主要用：json.dump / json.load / os.replace
# TodoManager 业务层      负责「规则怎么算」，主要用：add / list / done / remove / stats
# main 界面层             负责「命令怎么接」，主要用：argparse + print
#
# 【重点】每一层只依赖「下一层的接口」，不关心它的实现——这叫「面向接口编程」。


# ==============================================================================
# 知识点 2：存储层 —— 把列表安全地写进 JSON 文件
# ==============================================================================
#
# 【讲解】存储层要解决三个问题：文件不存在 → 返回空列表别报错；内容损坏 →
#   捕获 JSONDecodeError；写到一半断电 → 先写临时文件，再「原子替换」。
# 【重点】第三点最关键：直接打开原文件覆盖写，写到一半崩溃就全毁了。正确姿势是
#   「① 写 todos.json.tmp → ② os.replace 原子替换正式文件」，任何时刻硬盘上都是
#   一个完整的旧版本或完整的新版本。

print("\n--- 存储层 Storage ---")


class Storage:
    """存储层：只负责把列表存成 JSON 文件 / 从 JSON 文件读回列表。"""

    def __init__(self, path):
        self.path = path                      # 路径从外部传进来，方便测试
    def load(self):
        if not os.path.exists(self.path):     # 第一次运行，文件还不存在
            return []
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)           # 反序列化
        except json.JSONDecodeError:          # 文件被人手改坏了
            print(f"  [警告] {os.path.basename(self.path)} 不是合法 JSON，按空列表处理")
            return []

    def save(self, todos):
        tmp_path = self.path + ".tmp"         # 临时文件，写完再原子替换
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)   # 中文友好 + 缩进
        os.replace(tmp_path, self.path)       # 原子替换，比 remove + rename 安全


demo_dir = tempfile.mkdtemp(prefix="todo_")            # 演示用临时目录
demo_file = os.path.join(demo_dir, "todos.json")       # 演示用数据文件
storage = Storage(demo_file)
print(f"文件一开始存在吗：{os.path.exists(demo_file)}")
print(f"第一次 load 的结果：{storage.load()}")

# 存一条记录进去（字段要和真实待办一致，别只存一半，否则业务层会 KeyError）
storage.save([{"id": 1, "title": "验证存储层", "done": False,
               "priority": 2, "created": "2026-11-12 20:00"}])
print(f"save 之后文件存在吗：{os.path.exists(demo_file)}")
print(f"读回来：{storage.load()}")

# 输出：
# --- 存储层 Storage ---
# 文件一开始存在吗：False
# 第一次 load 的结果：[]
# save 之后文件存在吗：True
# 读回来：[{'id': 1, 'title': '验证存储层', 'done': False, 'priority': 2, 'created': '2026-11-12 20:00'}]
#
# 【重点】`load()` 在文件不存在时返回 []，不抛异常——这让「第一次使用」和
#   「用了一百次」的调用代码完全一样。【常见错误】把路径写死在类里（如
#   self.path = "todos.json"）：测试会弄脏工作目录，也没法操作多个清单。


# ==============================================================================
# 知识点 3：业务层 —— TodoManager 的增删改查
# ==============================================================================
#
# 【讲解】业务层管「待办这件事的规则」：新增自动分配 id（最大 id + 1）、标记完成、
#   按 id 删除、排序（未完成在前 → 优先级高在前 → id 小在前）、统计。
# 【重点】时间从构造参数 now_fn「注入」进来：若直接用 datetime.now()，每次运行输出
#   都不一样，注释里的输出就没法写死；传固定时钟，结果完全可复现。这叫「依赖注入」。

print("\n--- 业务层 TodoManager ---")

PRIORITY_NAME = {1: "高", 2: "中", 3: "低"}          # 优先级 → 中文名
FIXED_NOW = lambda: "2026-11-12 20:00"              # 演示专用的固定时钟


class TodoManager:
    """业务层：只管规则，不关心数据存在哪、界面长什么样。"""

    def __init__(self, storage, now_fn=None):
        self.storage = storage
        # 没传时钟就用真时间；传了就用传进来的（演示和测试用）
        self.now_fn = now_fn or (lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.todos = storage.load()                # 启动时把数据读进内存

    def _next_id(self):
        return max((t["id"] for t in self.todos), default=0) + 1   # 空列表从 1 开始

    def add(self, title, priority=2):
        todo = {"id": self._next_id(), "title": title, "done": False,
                "priority": priority, "created": self.now_fn()}
        self.todos.append(todo)
        self.storage.save(self.todos)               # 每次改动立刻落盘
        return todo

    def list_todos(self, show_done=True):
        """未完成在前 → 优先级高的在前 → id 小的在前。"""
        items = [t for t in self.todos if show_done or not t["done"]]
        return sorted(items, key=lambda t: (t["done"], t["priority"], t["id"]))

    def mark_done(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["done"] = True
                self.storage.save(self.todos)
                return True
        return False

    def remove(self, todo_id):
        before = len(self.todos)
        self.todos = [t for t in self.todos if t["id"] != todo_id]   # 推导式筛掉
        if len(self.todos) == before:                                # 长度没变=没找到
            return False
        self.storage.save(self.todos)
        return True

    def stats(self):
        total, done = len(self.todos), sum(1 for t in self.todos if t["done"])
        return {"total": total, "done": done,
                "rate": round(done / total * 100, 1) if total else 0.0,   # 防除零
                "urgent_left": sum(1 for t in self.todos
                                   if not t["done"] and t["priority"] == 1)}


manager = TodoManager(Storage(demo_file), now_fn=FIXED_NOW)   # 复用刚才那个文件
print(f"启动时读到的待办数：{len(manager.todos)}")

manager.add("买牛奶", priority=1)                    # 新增三条
manager.add("写 Python 作业", priority=2)
manager.add("看《地球脉动》", priority=3)
print("新增后（id / 标题 / 优先级）：")
for todo in manager.list_todos():
    print(f"  {todo['id']}  {todo['title']}  优先级：{PRIORITY_NAME[todo['priority']]}")

manager.mark_done(3)                                 # 把第 3 条标记完成
print(f"标记 3 号完成后，已完成数量：{sum(1 for t in manager.todos if t['done'])}")
print(f"删除 99 号成功吗：{manager.remove(99)}")
print(f"统计：{manager.stats()}")

# 输出：
# --- 业务层 TodoManager ---
# 启动时读到的待办数：1
# 新增后（id / 标题 / 优先级）：
#   2  买牛奶  优先级：高
#   1  验证存储层  优先级：中
#   3  写 Python 作业  优先级：中
#   4  看《地球脉动》  优先级：低
# 标记 3 号完成后，已完成数量：1
# 删除 99 号成功吗：False
# 统计：{'total': 4, 'done': 1, 'rate': 25.0, 'urgent_left': 1}
#
# 【重点】「启动时读到的待办数：1」就是知识点 2 存进去的那条，证明持久化生效了；
#   排序里 2 号（高）排在 1 号（中）前面，因为排序键第二个是 priority。
# 【常见错误】`max((t["id"] for t in ...), default=0)` 忘了写 default：空列表会抛
#   ValueError: max() iterable argument is empty。


# ==============================================================================
# 知识点 4：界面层 —— argparse 做命令行
# ==============================================================================
#
# 【讲解】argparse 做三件事：定义有哪些子命令、定义每个子命令有哪些参数、
#   自动生成 --help 并在参数出错时自动报错。# 【重点】add_subparsers(dest="command") 是「子命令」的关键，它让你能写
#   `todo add 买牛奶` 这种「动词 + 宾语」的工具；required=True 表示必须给子命令。

print("\n--- 界面层 argparse ---")


def build_parser():
    """构建命令行解析器。单独抽成函数，方便测试时复用。"""
    parser = argparse.ArgumentParser(prog="todo", description="一个简单的待办事项管理器")
    parser.add_argument("--data", default="todos.json", help="数据文件路径")
    sub = parser.add_subparsers(dest="command", required=True)     # 必须有子命令

    p_add = sub.add_parser("add", help="新增待办")
    p_add.add_argument("title", help="待办内容")
    p_add.add_argument("-p", "--priority", type=int, choices=[1, 2, 3], default=2,
                       help="优先级：1 高 / 2 中 / 3 低")
    p_list = sub.add_parser("list", help="列出待办")
    p_list.add_argument("--all", action="store_true", help="连已完成的也显示")
    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("id", type=int, help="待办编号")
    p_remove = sub.add_parser("remove", help="删除待办")
    p_remove.add_argument("id", type=int, help="待办编号")
    sub.add_parser("stats", help="查看统计")
    return parser


def run_cli(argv, now_fn=None):
    """执行一条命令。argv 是字符串列表，比如 ["add", "买牛奶", "-p", "1"]。"""
    args = build_parser().parse_args(argv)                 # 解析参数
    mgr = TodoManager(Storage(args.data), now_fn=now_fn)   # 真实使用时用真时钟

    if args.command == "add":
        todo = mgr.add(args.title, args.priority)
        print(f"已添加 #{todo['id']}：{todo['title']}（优先级 {PRIORITY_NAME[todo['priority']]}）")
    elif args.command == "list":
        items = mgr.list_todos(show_done=args.all)
        if not items:
            print("（还没有待办，用 add 添加一条吧）")
            return
        for todo in items:
            mark = "✓" if todo["done"] else " "
            print(f"[{mark}] #{todo['id']} {todo['title']}  (P{PRIORITY_NAME[todo['priority']]})")
    elif args.command == "done":
        print(f"标记 #{args.id} 完成：{'成功' if mgr.mark_done(args.id) else '没找到这条'}")
    elif args.command == "remove":
        print(f"删除 #{args.id}：{'成功' if mgr.remove(args.id) else '没找到这条'}")
    else:
        s = mgr.stats()
        print(f"共 {s['total']} 条，已完成 {s['done']} 条（{s['rate']}%），"
              f"待办中的高优先级有 {s['urgent_left']} 条")


# 演示：直接用 argv 列表调用，不用真的敲命令（这样输出才可复现）
run_cli(["--data", demo_file, "add", "交周报", "-p", "1"], now_fn=FIXED_NOW)
run_cli(["--data", demo_file, "list"], now_fn=FIXED_NOW)
run_cli(["--data", demo_file, "stats"], now_fn=FIXED_NOW)

# 输出：
# --- 界面层 argparse ---
# 已添加 #5：交周报（优先级 高）
# [ ] #2 买牛奶  (P高)
# [ ] #5 交周报  (P高)
# [ ] #1 验证存储层  (P中)
# [ ] #4 看《地球脉动》  (P低)
# 共 5 条，已完成 1 条（20.0%），待办中的高优先级有 2 条
#
# 【注意】`list` 默认只显示未完成的，要连已完成一起看得加 --all。
# 【重点】argparse 免费帮你做了这些事（在终端里试试）：--help 看全局帮助、
#   `add --help` 看子命令帮助、`add x -p 9` 自动报错「9 不在 [1,2,3] 里」。

# ==============================================================================
# 知识点 5：验证持久化 + __main__ 入口 + 清理现场
# ==============================================================================
#
# 【讲解】程序重启后数据还在吗？这是持久化唯一的验收标准。验证方法：新建一个
#   TodoManager（相当于重启程序），看它能不能读到刚才的数据。
# 【重点】三步套路：① 写入 → ② 新建对象/重启进程 → ③ 读回来与写入一致。

print("\n--- 验证持久化 ---")

fresh = TodoManager(Storage(demo_file), now_fn=FIXED_NOW)     # 全新对象 = 模拟重启
print(f"重新打开后读到几条：{len(fresh.todos)}")
print(f"第一条的标题是：{fresh.todos[0]['title']}")
with open(demo_file, encoding="utf-8") as f:                  # 看文件的真实内容
    raw = json.load(f)
print(f"原始数据的第一条：{raw[0]}")

# 输出：
# --- 验证持久化 ---
# 重新打开后读到几条：5
# 第一条的标题是：验证存储层
# 原始数据的第一条：{'id': 1, 'title': '验证存储层', 'done': False, 'priority': 2, 'created': '2026-11-12 20:00'}
#
# 【重点】`raw[0]` 显示 JSON 文件里的真实内容：id、title、done、priority、created
#   五个字段，都是 JSON 支持的类型。
# 【常见错误】只改内存、忘了调 save()：看着对，程序一关就没了。
#   【记法】凡是「改用户数据」，最后一步永远是「落盘」。下面是入口与收尾。

print("\n--- __main__ 入口 ---")
print(f"本文件的 __name__ 是：{__name__}")
print(f"是直接运行吗：{__name__ == '__main__'}")
print(f"收到几个命令行参数（含脚本名）：{len(sys.argv)}")
print("提示：真要用它请带上参数运行，比如 add '买菜'")

# 输出：
# --- __main__ 入口 ---
# 本文件的 __name__ 是：__main__
# 是直接运行吗：True
# 收到几个命令行参数（含脚本名）：1
# 提示：真要用它请带上参数运行，比如 add '买菜'
#
# 【重点】len(sys.argv) == 1 说明只给了脚本名、没给参数，所以本文件选择跑演示。
# 【常见错误】把 `if __name__ == "__main__":` 写成 `if __name__ = "__main__":`
#   （少个等号）会报 SyntaxError；写成 "main"（少下划线）则永远不执行主流程，
#   而且不报错——这种 bug 最难查。


def main(argv=None):
    """真正的入口：有参数就干活，没参数就打印用法提示。"""
    argv = sys.argv[1:] if argv is None else argv   # None 表示用真实命令行参数
    if argv:                                        # 用户给了参数 → 当工具用
        run_cli(argv)
    else:                                           # 没参数 → 打印用法提示
        print("这是演示模式。真要用它请带上参数，例如：")
        print("  python 05_综合实战项目.py --data my.json add '买牛奶' -p 1")
        print("  python 05_综合实战项目.py --data my.json list")


print("\n--- 数据文件的真实片段 ---")
with open(demo_file, encoding="utf-8") as f:
    raw_text = f.read()
print(f"文件大小：{len(raw_text)} 字节")
print(raw_text[:120].replace("\n", "⏎"))          # 换行显示成符号，一行看完
shutil.rmtree(demo_dir, ignore_errors=True)       # 连目录一起删
print(f"临时目录已清理：{not os.path.exists(demo_dir)}")

# 输出：
# --- 数据文件的真实片段 ---
# 文件大小：585 字节
# [⏎  {⏎    "id": 1,⏎    "title": "验证存储层",⏎    "done": false,⏎    "priority": 2,⏎    "created": "2026-11-12 20:00"⏎  },⏎  
# 临时目录已清理：True
#
# 【注意】JSON 里的布尔值是小写 false，Python 里是 False——第 03 个文件讲的「语言
#   差异」，落盘时被 json 自动转换了。读文件的 open() 记得写 encoding="utf-8"，
#   Windows 上不写会按 GBK 打开，遇到中文报 UnicodeDecodeError。

if __name__ == "__main__":
    main()


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 分层设计：存储层只管落盘、业务层只管规则、界面层只管交互，各自可替换
# 2. Storage 三件事：文件不存在返回空列表、JSON 损坏要捕获、写入用原子替换
# 3. 原子写入：先写 .tmp 再 os.replace，保证任何时刻文件都是完整的
# 4. 依赖注入：路径和时钟从外面传进来，代码才能测试、输出才可复现
# 5. 排序用 sorted(..., key=lambda t: (...)) 做多级排序，简洁可读
# 6. argparse 的 subparsers 做「动词 + 宾语」命令，还免费送 --help 和错误提示
# 7. 持久化验证三步：写入 → 新建对象 → 读回比对；改数据后最后一步永远是 save()
# 8. if __name__ == "__main__": main() 让同一文件既能当工具又能当教程
# 9. 这个文件用的全部知识都来自第 1~4 个文件——这就是「综合」


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：给 add 增加 --due 参数（截止日期 2026-12-01），存进 JSON，
#         并在 list 里显示「还剩几天」。
# 练习 2：给 list 增加 --sort 参数，可以按 id / 优先级 / 创建时间 排序；
#         再加一个 search 子命令，按关键字模糊搜索待办标题。
# 练习 3：把「已完成」的条目归档到 archive.json，让 todos.json 只留未完成的。
# 练习 4：把这个文件拆成真正的包（参考第 02 个文件）：todo/__init__.py、
#         todo/storage.py、todo/manager.py、todo/__main__.py，
#         然后用 python -m todo list 运行它。
#
# 【下一步】恭喜完成第 12 章！接下来是第 13 章：测试与调试。
# ==============================================================================
