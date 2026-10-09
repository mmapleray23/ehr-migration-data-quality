# Mac 上一步一步建立你的 EHR migration 项目

## 目标

先运行 starter，理解每一步，然后亲手增加规则和报告。项目既展示数据工程
（转换、关联、质量、核对），也展示实施咨询（需求、映射、异常处理和验收）。
目前是规则驱动的项目；不要在简历上称为已训练的 AI 模型。

## 1. 准备文件

解压项目压缩包。把 `ehr-migration-data-quality` 文件夹放到 Mac 桌面。
确保文件夹里面直接有 README.md、app.py、src、data、docs、tests、outputs。
不要把整个文件夹又放入一个同名文件夹。

## 2. 确认 Python

Spotlight 搜索 Terminal（终端）。运行：

```bash
python3 --version
```

建议 Python 3.11 或 3.12。如没有 Python，到 https://www.python.org/downloads/
安装 macOS 的 Python 3.12，关闭并重新打开终端后检查。
如果同时有多个 Python，可在创建环境时明确用 `python3.12 -m venv .venv`。

## 3. 进入文件夹并安装

下列命令逐行执行。假设文件夹放在桌面：

```bash
cd ~/Desktop/ehr-migration-data-quality
pwd
ls
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

pwd 显示路径，ls 应显示 app.py 和 requirements.txt。如果桌面路径不同，输入
`cd `（末尾留一个空格），把 Finder 中的项目文件夹拖到终端，再按回车。
.venv 是这个项目独立使用的环境，不需要上传。每次重新打开终端，进入项目后
再次运行 `source .venv/bin/activate`。

## 4. 运行 pipeline

```bash
python -m src.pipeline
```

打开 outputs/reconciliation.csv。默认数据应有 101 条客户来源记录和 201 条
入院来源记录。每个表的 input_rows 应等于 ready_rows + review_rows。
summary.json 的 rule_violations 是错误次数，不是有问题的客户人数。

依次打开原始数据、ready、review 和 exceptions，追踪同一条记录为什么进入
某个输出。客户重复 ID 的所有记录都进入 review；相关 admission 也暂停导出。

## 5. 验证关键行为

```bash
python -m unittest discover -s tests -v
```

应看到 6 项测试通过、结尾 OK。它们覆盖前导零、开放入院、重复客户依赖、
孤立客户、未知代码、日期逻辑、冲突映射、缺失字段等关键行为。
测试通过只证明这些定义好的行为，不证明真实客户资料准确。

## 6. 打开网页 demo

```bash
python -m streamlit run app.py
```

浏览器打开终端显示的 Local URL，通常是 http://localhost:8501。
点击 Run validation，查看总行数、ready/review 数量、错误图表、筛选与下载。
只有内置模拟数据，没有上传患者资料功能。终端 Ctrl+C 停止网页。

## 7. 第一个亲手做的练习：新增未知项目代码

先保存当前文件。使用代码编辑器把 data/raw/admissions.csv 中一条正常记录的
program_code 改成 NEW_UNKNOWN。注意选一条 client_id=00001 且其他字段有效的记录。
再次运行 pipeline。它应从 ready 进入 review，并出现 unmapped_program。

随后在 data/reference/program_mapping.csv 新增一行：

```csv
NEW_UNKNOWN,NEW01
```

再次运行，确认该条记录恢复 ready。记录前后变化。这展示你理解“发现问题 →
核实并补充映射 → 重新验证”的工作，而不只是执行代码。
注意：真实工作必须先获得业务负责人批准，不能凭空指定项目对应关系。

如要恢复内置数据：

```bash
python -m src.generate_data
python -m src.pipeline
```

generate_data 会覆盖三个输入文件，先备份或提交你想保留的修改。

## 8. 第二个练习：新增未来出生日期规则

在 src/pipeline.py 找到客户日期检查位置。新增 future_dob 检查，把晚于参考
日期的出生日期放入 review。把参考日期作为 validate 的参数，不要在测试里
依赖每天变化的系统时间。给 tests/test_pipeline.py 增加一个测试：未来 DOB
客户不能进入 ready，其 admission 必须同步进入 review。然后重新跑全部测试。

先自己写，再用 AI 解释或检查。你需要能解释为什么未来 DOB 不自动修改。

## 9. 第三个练习：新增业务核对

按 target_program_code 和 admit_date 的月份汇总 ready admissions 数量，导出
program_month_summary.csv。讲清它只统计 ready 记录；review 未计入，不能当作
完整服务量。没有服务或 billing 数据时，不要把 admission 数量称为服务次数或收入。

## 10. 上传到 GitHub（建议 GitHub Desktop）

下载 https://desktop.github.com/ 并登录 mmapleray23。

如果还没建立项目仓库：

1. GitHub 网页创建 ehr-migration-data-quality，Public，勾选 README。
2. GitHub Desktop：File → Clone repository，选择这个仓库，选择本地位置，Clone。
3. 把 starter 文件夹里面的内容复制到克隆出来的文件夹，保留克隆仓库的 Git 配置。
4. Desktop 的 Changes 里检查文件。不要加入 .venv、真实资料、密钥。
5. Summary 填 Add synthetic EHR migration pipeline and validation demo。
6. Commit to main，然后 Push origin。

如果仓库已经建立，直接从第 2 步开始。以后只修改这个克隆目录中的文件，
修改后测试、Commit、Push，避免维护两个不同副本。

## 11. 链接个人主页

在个人网站仓库的 index.html 中，把项目卡片链接设成：
https://github.com/mmapleray23/ehr-migration-data-quality

标题 EHR Migration & Data Quality Pipeline。
描述：Synthetic-data demonstration of EHR mapping, validation, and reconciliation.
工具 Python / pandas / Streamlit。完成练习前标注 Learning project / In progress。

GitHub Pages 展示个人主页；Python demo 要单独运行或部署。

## 12. 稍后发布在线 demo

先确认 GitHub 仓库全部为模拟资料。按照 Streamlit Community Cloud 官方教程：
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
选择该 GitHub 仓库、main 分支、app.py，使用 requirements.txt 安装依赖。
发布后在无登录浏览器窗口检查按钮、筛选和下载，再将实际链接加到主页。
本 starter 未替你进行在线部署，也未验证你的 Mac 环境。

## 常见问题

| 提示 | 处理 |
|---|---|
| No module named pandas / streamlit | 激活 .venv，然后 python -m pip install -r requirements.txt |
| No module named src | cd 到包含 src 与 app.py 的项目根目录 |
| 找不到 requirements.txt | 用 pwd 和 ls 确认当前目录 |
| Port 8501 in use | 停止之前的 app，或运行时加 --server.port 8502 |
| 日期突然变成空值 | 看 exceptions；源文件仍保留原值，失败日期不会自动修正 |
| 修改输入后网页仍显示旧结果 | 再点 Run validation |

## 面试时应该能解释

为什么 ID 必须作为文本？为什么重复客户不能简单保留第一条？为什么客户
未通过检查会阻止 admission？错误次数为什么多于异常行数？数量平衡为什么
不等于内容正确？业务人员和 Data Team 各自负责什么？你的代码做了哪些事，
哪些是 starter/AI 辅助生成的，哪些是你独立扩展的？
