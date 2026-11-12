"""
================================================================================
第 12 章 · 模块与标准库
文件 04：第三方库入门
================================================================================

【学习目标】
    1. 分清标准库和第三方库，知道为什么需要 pip
    2. 学会用 pip 安装 / 查看 / 卸载包
    3. 跑通 requests 和 numpy 两个最常用的第三方库
    4. 学会用 requirements.txt 管理项目依赖（版本号里的 ~= >= == 怎么选）
    5. 理解虚拟环境为什么必须用

【怎么用这个文件】
    - 每个知识点一小节，从上往下读
    - 本文件不会真的联网！requests 那节用「本地服务器」演示，安全又稳定
    - 如果你的机器没装 requests / numpy，相关小节会自动跳过并提示怎么装
    - 直接运行：python 04_第三方库入门.py

【前置知识】
    - 本文件 03_常用标准库.py（json、os 在这里还会用到）
================================================================================
"""

import sys                          # 查标准库列表、启动子进程
import json                         # 解析接口返回的 JSON
import os                           # 拼路径
import tempfile                     # 建临时目录写 requirements.txt
import shutil                       # 删临时目录
import threading                    # 起线程跑本地 HTTP 服务
from http.server import HTTPServer, BaseHTTPRequestHandler   # 本地服务器


# ==============================================================================
# 知识点 1：标准库 vs 第三方库 —— 自带电池 vs 去超市买
# ==============================================================================
#
# 【讲解】Python 号称「自带电池」（batteries included）：装了 Python 就自带
#   几百个标准库（os、json、datetime……），开箱即用。
#   但标准库不可能什么都有。别人写好的、能解决特定问题的包，叫第三方库：
#    requests 发 HTTP 请求、numpy 数组和矩阵运算（比 list 快几十倍）、
#    pandas 表格数据处理、django 做网站。它们都要用 pip 从网上下载安装。
# 【重点】判断一个模块是不是标准库，两招：
#       1. '名字' in sys.stdlib_module_names
#       2. import 一下，报 ModuleNotFoundError 就是没装

print("--- 标准库 vs 第三方库 ---")
print(f"os 是标准库吗：{'os' in sys.stdlib_module_names}")
print(f"json 是标准库吗：{'json' in sys.stdlib_module_names}")
print(f"requests 是标准库吗：{'requests' in sys.stdlib_module_names}")
print(f"numpy 是标准库吗：{'numpy' in sys.stdlib_module_names}")
print(f"标准库一共有多少个模块：{len(sys.stdlib_module_names) > 200}（超过 200 个）")

# 输出：
# --- 标准库 vs 第三方库 ---
# os 是标准库吗：True
# json 是标准库吗：True
# requests 是标准库吗：False
# numpy 是标准库吗：False
# 标准库一共有多少个模块：True（超过 200 个）
#
# 【注意】`sys.stdlib_module_names` 是 Python 3.10 才有的，3.9 及以前没有它。
# 【常见错误】以为「import 不报错就是标准库」。requests 装好后 import 也不报错，
#   但它依然是第三方库。【记法】标准库 = 跟 Python 一起装的，第三方库 = pip 装的。


# ==============================================================================
# 知识点 2：pip 是命令行工具，不是 Python 代码
# ==============================================================================
#
# 【讲解】这是新手第一个大坑：pip 要在「命令行/终端」里敲，不能写进 .py 文件！
#   常用命令（在终端里）：
#       pip install requests             装
#       pip install requests==2.31.0     装指定版本
#       pip install -r requirements.txt  按清单装
#       pip list / pip show requests     看装了哪些 / 看某个包的详情
#       pip uninstall requests           卸载
#       pip install --upgrade requests   升级
# 【重点】如果 pip 命令找不到，用 `python -m pip` 代替，永远有效：它明确表示
#   「用当前这个 Python 解释器跑 pip 模块」，能避免「pip 装到另一个 Python 里」的惨案。
# 【重点】在 .py 里想装包，只能 subprocess 调 pip（不推荐，仅了解）：
#       subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
#
# 下面演示的是「查看 pip 版本」——唯一安全、不联网的 pip 操作：

print("\n--- pip 是命令行工具 ---")

import subprocess                   # subprocess：在 Python 里调用外部命令

pip_result = subprocess.run(
    [sys.executable, "-m", "pip", "--version"],   # 用「当前解释器」跑 pip
    capture_output=True,                          # 抓回输出
    text=True,                                    # 文本模式
    encoding="utf-8",                             # 防中文乱码
)
print(f"pip 命令的退出码：{pip_result.returncode}")
print(f"能读到 pip 版本信息吗：{'pip' in pip_result.stdout.lower()}")
print("提示：真正的安装命令要在终端里敲，比如  pip install requests")

# 输出：
# --- pip 是命令行工具 ---
# pip 命令的退出码：0
# 能读到 pip 版本信息吗：True
# 提示：真正的安装命令要在终端里敲，比如  pip install requests
#
# 【注意】退出码 0 表示命令成功；非 0 表示出错（比如找不到 pip、没联网）。
# 【常见错误】在 .py 里写 `pip install requests` —— 这是语法错误！pip 不是 Python
#   语句，它是操作系统的命令。【记法】pip 属于「终端」，import 属于「.py 文件」。


# ==============================================================================
# 知识点 3：import 第三方库 —— 和标准库一模一样的用法
# ==============================================================================
#
# 【讲解】好消息：第三方库装好之后，import 的写法和标准库没有任何区别。
#   Python 不区分模块从哪来，都从 sys.path 里找（第 01 个文件讲过）。
# 【重点】第三方库装在 site-packages 目录里，那个目录也在 sys.path 里，
#   所以 import 时能找到。

print("\n--- import 第三方库 ---")

try:
    import requests                                    # 试试能不能导入
    HAS_REQUESTS = True
    print(f"requests 装好了，版本：{requests.__version__}")
    print(f"它装在：{os.path.basename(os.path.dirname(requests.__file__))} 目录下")
except ImportError:
    HAS_REQUESTS = False
    print("requests 还没装，本文件里和它相关的演示会自动跳过")
    print("安装命令：pip install requests")

# 输出：
# --- import 第三方库 ---
# requests 装好了，版本：2.34.2
# 它装在：requests 目录下
#
# 【注意】版本号（2.34.2）和目录名会随你的环境变化，以实际输出为准。
# 【重点】用 try / except ImportError 包住 import，是「可选依赖」的标准写法：
#   即使别人没装这个库，你的程序也不会直接崩，而是优雅降级。


# ==============================================================================
# 知识点 4：requests 实战 —— 发 HTTP 请求
# ==============================================================================
#
# 【讲解】requests 的官方口号是「HTTP for Humans」（给人类用的 HTTP）。
#   标准库也有 urllib，但那个像「用螺丝刀拧螺丝」，requests 像「电动螺丝刀」。
#   最常用的四个动作：requests.get(网址) 拿数据；requests.post(网址, json=数据)
#   提交数据；resp.status_code 看状态码（200 成功 / 404 找不到 / 500 服务器崩）；
#   resp.json() 把返回的 JSON 直接变成 Python 字典。
# 【重点】我【不会】真的访问外网！而是在本地起一个临时 HTTP 服务器，
#   这样演示能跑通、不依赖网络、也不给别人的服务器发垃圾请求。
#   这本身就是好习惯：测试网络代码时，用本地假服务器（mock server）。

print("\n--- requests：发 HTTP 请求 ---")


class TodoHandler(BaseHTTPRequestHandler):
    """一个假的待办接口：收到任何 GET 都返回一条固定的待办。"""

    def do_GET(self):
        payload = {"code": 0, "data": {"id": 1, "title": "买牛奶", "done": False}}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")   # 转成字节
        self.send_response(200)                                          # 状态码 200
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))               # 必须告诉长度
        self.end_headers()
        self.wfile.write(body)                                           # 写回响应体

    def log_message(self, *args):
        pass                                    # 关掉默认的日志打印，免得刷屏


if HAS_REQUESTS:
    server = HTTPServer(("127.0.0.1", 0), TodoHandler)   # 端口写 0 = 让系统随机分配
    port = server.server_address[1]                      # 拿回真正分配到的端口
    thread = threading.Thread(target=server.serve_forever, daemon=True)  # 后台跑
    thread.start()

    resp = requests.get(f"http://127.0.0.1:{port}/api/todo/1", timeout=5)  # 最多等 5 秒
    print(f"状态码：{resp.status_code}")
    print(f"请求成功吗（ok 属性）：{resp.ok}")
    print(f"响应头 Content-Type：{resp.headers['Content-Type']}")
    print(f"返回的 JSON：{resp.json()}")
    print(f"直接取字段：{resp.json()['data']['title']}")
    print(f"resp.json() 的类型：{type(resp.json()).__name__}")

    server.shutdown()                          # 关掉服务器（别忘了！）
    print("本地假服务器已关闭")
else:
    print("（跳过：requests 未安装）")

# 输出：
# --- requests：发 HTTP 请求 ---
# 状态码：200
# 请求成功吗（ok 属性）：True
# 响应头 Content-Type：application/json; charset=utf-8
# 返回的 JSON：{'code': 0, 'data': {'id': 1, 'title': '买牛奶', 'done': False}}
# 直接取字段：买牛奶
# resp.json() 的类型：dict
# 本地假服务器已关闭
#
# 【重点】`resp.json()` 就是「自动帮你 json.loads(resp.text)」，省了手动解析，
#   这是 requests 最贴心的功能之一。
# 【重点】`port = 0` 是「让操作系统分配一个空闲端口」的技巧，写死 8080 容易撞端口。
# 【常见错误】三个新手必踩的坑：
#   1. 不写 timeout：服务器不回你就永远卡住（默认是无限等待！）
#   2. 不看 status_code：404/500 时 resp.json() 可能直接抛异常
#   3. HTTPS 证书报错：内网自签证书才需要 verify=False（生产环境别这么干）


# ==============================================================================
# 知识点 5：numpy 实战 —— 比 list 快几十倍的数组
# ==============================================================================
#
# 【讲解】numpy 的核心是 ndarray（N 维数组）。为什么快？因为它把数据存在一整块
#   连续内存里，并且用 C 语言写的循环批量运算；而 Python 的 list 是「指针数组」，
#   每个元素都是一次对象查找，慢得多。
# 【重点】numpy 最强大的两个特性：向量化（a * 2 直接整组乘 2，不用 for 循环）
#   和布尔索引（a[a > 2] 直接筛出满足条件的元素）。
# 【注意】numpy 是第三方库，未安装时本节的输出会变成提示信息。

print("\n--- numpy：数组运算 ---")

try:
    import numpy as np                                  # 社区惯例：永远写成 np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("（跳过：numpy 未安装，安装命令 pip install numpy）")

if HAS_NUMPY:
    a = np.array([1, 2, 3, 4, 5])                       # 从 list 建数组
    print(f"数组：{a}")
    print(f"dtype={a.dtype}，ndim={a.ndim}，shape={a.shape}")
    print(f"平均值={a.mean()}，总和={a.sum()}，标准差={round(float(a.std()), 4)}")
    print(f"向量化 a * 2：{a * 2}")                      # 不用 for 循环，整组乘 2
    print(f"布尔索引 a[a > 2]：{a[a > 2]}")              # 直接筛选
    print(f"arange(0, 10, 3)：{np.arange(0, 10, 3)}")     # 类似 range，但返回数组
    print(f"linspace(0, 1, 5)：{np.linspace(0, 1, 5)}")   # 5 等分点
    m = np.array([[1, 2, 3], [4, 5, 6]])                 # 二维数组（矩阵）
    print(f"二维数组 shape：{m.shape}，转置后 shape：{m.T.shape}")
    print(f"转置结果：{m.T.tolist()}")
    print(f"numpy 版本：{np.__version__}")

# 输出：
# --- numpy：数组运算 ---
# 数组：[1 2 3 4 5]
# dtype=int64，ndim=1，shape=(5,)
# 平均值=3.0，总和=15，标准差=1.4142
# 向量化 a * 2：[ 2  4  6  8 10]
# 布尔索引 a[a > 2]：[3 4 5]
# arange(0, 10, 3)：[0 3 6 9]
# linspace(0, 1, 5)：[0.   0.25 0.5  0.75 1.  ]
# 二维数组 shape：(2, 3)，转置后 shape：(3, 2)
# 转置结果：[[1, 4], [2, 5], [3, 6]]
# numpy 版本：2.5.4
#
# 【注意】输出里数组用空格分隔、没有逗号，这是 numpy 的打印风格。
#   dtype 在 Windows 上通常是 int64，部分系统上是 int32，以实际为准。
# 【重点】shape=(5,) 那个逗号不是打错：它是「只有一维」的元组，表示长度 5。
#   （5）会被当成整数 5，(5,) 才是元组。
# 【常见错误】忘了 import numpy as np 就写 np.array —— NameError。另外别把文件名
#   起成 numpy.py，否则会遮蔽真正的 numpy（第 01 个文件讲过）。


# ==============================================================================
# 知识点 6：版本管理与 requirements.txt
# ==============================================================================
#
# 【讲解】为什么一定要锁版本？因为第三方库会升级，而升级可能改 API。
#   你昨天写的代码今天跑不了，很可能就是某个库悄悄升级了（江湖人称「依赖地狱」）。
#   requirements.txt 就是「依赖清单」，一行一个包，四种写法：
#       requests            不锁版本：装最新的（危险！）
#       requests==2.31.0    精确锁定：团队每个人装到的都一模一样（推荐）
#       requests>=2.28.0    最低版本：至少这么新
#       requests~=2.31.0    兼容版本：>=2.31.0 且 <2.32.0（允许修 bug 的小版本）
# 【重点】版本号规则叫「语义化版本」（SemVer）：主版本.次版本.修订号。
#   2.31.5 → 2 是主版本（大改、会不兼容）、31 是次版本（加功能）、5 是修 bug。
# 【重点】== 最稳（团队一致），>= 最松（容易踩坑），~= 是折中。
#   项目上线/交付时，一律用 == 锁死。

print("\n--- 版本管理与 requirements.txt ---")

# 把一份真实的 requirements.txt 写到临时目录，看看它长什么样
tmp_dir = tempfile.mkdtemp(prefix="req_")
req_path = os.path.join(tmp_dir, "requirements.txt")

req_content = """# 待办管理器项目的依赖清单
requests==2.34.2        # 发 HTTP 请求
numpy==2.5.4            # 数组运算
# 下面两行演示版本约束的其他写法
pytest>=8.0.0           # 测试框架，至少 8.0
python-dateutil~=2.9.0  # 日期工具，2.9.x 系列
"""

with open(req_path, "w", encoding="utf-8") as f:      # 写文件，指定 utf-8
    f.write(req_content)

with open(req_path, encoding="utf-8") as f:           # 读回来逐行分析
    lines = f.readlines()

print(f"清单文件名叫：{os.path.basename(req_path)}")
print(f"总行数：{len(lines)}")

# 统计一下有效依赖（跳过空行和注释）
deps = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
print(f"有效依赖数：{len(deps)}")
for dep in deps:
    print(f"  - {dep.split('#')[0].strip()}")

# 输出：
# --- 版本管理与 requirements.txt ---
# 清单文件名叫：requirements.txt
# 总行数：6
# 有效依赖数：4
#   - requests==2.34.2
#   - numpy==2.5.4
#   - pytest>=8.0.0
#   - python-dateutil~=2.9.0
#
# 【重点】装清单里的依赖（在终端里跑）：pip install -r requirements.txt
#   生成清单（把当前环境冻结下来）：pip freeze > requirements.txt
# 【注意】pip freeze 会把「所有」包都写进去，包括别人的依赖。项目里通常只手工
#   维护「直接依赖」，用 pip-tools 之类的工具自动推导全量清单。
# 【常见错误】requirements.txt 里写 requests=2.31.0（只有一个等号）：pip 会把它
#   当成非法版本说明、直接报错。【记法】版本约束永远是双等号 ==。

shutil.rmtree(tmp_dir, ignore_errors=True)   # 清理临时目录


# ==============================================================================
# 知识点 7：虚拟环境 —— 换个项目就换一套依赖
# ==============================================================================
#
# 【讲解】假设你有两个项目：A 需要 requests 2.31、B 需要 requests 2.34。
#   如果都装在「全局」环境里，两个版本会打架，你只能保一个。
#
#   虚拟环境（venv）就是给每个项目一个「独立的包收纳箱」：
#       python -m venv .venv            创建虚拟环境
#       .venv\Scripts\activate          Windows 激活（Linux: source .venv/bin/activate）
#       pip install requests            这时装在 .venv 里，不影响全局
#       deactivate                      退出
#
# 【重点】激活后命令行前面会出现 (.venv) 提示，看到它就说明你在虚拟环境里。
# 【重点】.venv 目录不要提交到 git（体积大、和本机绑定），写进 .gitignore。

print("\n--- 虚拟环境 ---")
print(f"当前解释器路径的最后一段：{os.path.basename(sys.executable)}")
print(f"是在虚拟环境里吗：{sys.prefix != sys.base_prefix}")
has_site = any("site-packages" in p for p in sys.path)     # 先算好，别塞进 f-string
print(f"包安装目录（site-packages）在 sys.path 里吗：{has_site}")

# 输出：
# --- 虚拟环境 ---
# 当前解释器路径的最后一段：python.exe
# 是在虚拟环境里吗：False
# 包安装目录（site-packages）在 sys.path 里吗：True
#
# 【重点】判断「我在不在虚拟环境里」的万能写法：sys.prefix != sys.base_prefix
#   （True 就在虚拟环境里）。本文件是用系统 Python 跑的，所以输出 False。
# 【常见错误】用 IDE 时换了虚拟环境，但终端的 python 还是全局的，于是「明明装了
#   却 import 不到」。检查方法：print(sys.executable) 看路径对不对。这是新手最高频的
#   「玄学 bug」之一。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 标准库随 Python 安装，第三方库要用 pip 装；判断方法：sys.stdlib_module_names
# 2. pip 是命令行工具，不能写进 .py；找不到 pip 就用 python -m pip（更可靠）
# 3. 第三方库装好后，import 用法和标准库完全一样（都在 sys.path 里）
# 4. 用 try / except ImportError 包住第三方 import，实现可选依赖
# 5. requests 常用：get/post、status_code、resp.json()、timeout（必写！）
# 6. 测试网络代码用本地假服务器，不联网、不打扰别人、结果稳定
# 7. numpy 核心优势：向量化运算和布尔索引，比 for 循环快得多
# 8. 版本约束：== 精确（推荐交付用）、>= 最低、~= 兼容某系列；永远别写单等号
# 9. requirements.txt 记依赖，pip install -r 安装，pip freeze > 生成
# 10. 虚拟环境给每个项目独立依赖；sys.prefix != sys.base_prefix 可判断是否启用


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：在终端里执行 pip install requests，然后用 pip show requests
#         看看版本、安装位置、依赖项。再用 pip uninstall requests 卸载它。
# 练习 2：给自己的小项目建一个虚拟环境（python -m venv .venv），激活后
#         装一个包，再 deactivate，确认全局环境里没这个包。
# 练习 3：用 numpy 生成 10 个 0~100 的随机整数（np.random），
#         算出平均值、最大值，并把大于平均值的元素筛出来。
# 练习 4：写一个 requirements.txt，包含 requests 和 numpy，
#         用 pip install -r 安装，再用 pip freeze 看看生成的结果有什么不同。
#
# 【下一步】05_综合实战项目.py
# ==============================================================================
