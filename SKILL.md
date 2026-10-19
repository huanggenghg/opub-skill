---
name: opub-cli
description: Use when 用户要用 opub 发布/上传视频或图文、配置多平台发布、发布到抖音/小红书/快手/微博/B站/视频号/百家号，或排查 opub、账号登录校验、浏览器驱动环境问题
version: "0.9.13"
---

# opub CLI 使用指南

## 这是什么

`opub` 是一个 pip 包，把视频/图文一键发布到 7 个国内平台。本文件是它对 Agent 的完整接口契约：安装、配置、调用、读取结果所需的信息全部在此或 `opub` 运行时输出中。

## 安装

安装前先检测当前解释器。仅支持 CPython 3.11、3.12、3.13，以及 macOS arm64/x86_64、Windows x86_64、Linux x86_64；Skill 本身不提供或管理 Python。环境不匹配时向用户报告 `ENV-001` 和支持范围，不尝试从源码构建：

```bash
python -c "import platform,sys; assert platform.python_implementation() == 'CPython' and (3,11) <= sys.version_info[:2] <= (3,13); print(platform.system(), platform.machine())"
python -m pip install --only-binary=:all: "opub==0.9.13"
opub --repair-env
```

升级：`python -m pip install -U --only-binary=:all: opub`，升级后用 `opub --version` 确认版本。若 pip 报告没有匹配的发行版，不得移除 `--only-binary` 或改装源码包；应报告当前系统、CPU、Python 版本及上述支持范围。

**首次购买另需支付依赖：**安装本技能或 Python 包不会自动安装支付宝能力。需要购买或继续付款时，必须按下文“支付依赖检查”补齐 `alipay-payment-skill`、钱包授权所需的 `alipay-authenticate-wallet` 和 `alipay-bot` CLI；WorkBuddy 等宿主也适用。已有有效许可或已验付只待交付时不要求安装支付依赖。进入自动购买流程前，用 `opub --version` 确认实际运行时不低于 0.9.13，旧版须先升级。

系统依赖：

```bash
# 浏览器驱动（--repair-env 会安装，也可单独执行以下命令）
PLAYWRIGHT_CHROMIUM_DOWNLOAD_HOST="https://cdn.playwright.dev" patchright install chromium

# ffmpeg（仅"图文转视频"功能需要）
# macOS: brew install ffmpeg
# Ubuntu/Debian: sudo apt-get install ffmpeg
```

发布和环境 / 许可命令会在当前系统用户的 `~/.opub/` 创建数据目录（cookies、许可证和发布记录等），无需手动初始化。`--history` 不创建目录或文件。同一系统用户下的所有 Agent 固定使用这一目录；不要设置 `SAU_HOME`，也不要复制登录快照到工作区。

发布预检只检查环境，不安装或更新依赖。需要修复时运行 `opub --repair-env`；图文转视频使用 `opub --repair-env --with-video` 安装可选依赖，也可安装 `python -m pip install --only-binary=:all: "opub[video]"`。修复命令使用 opub 当前解释器，不需要许可，也不会发布内容；不能和发布参数或激活命令混用。修复可能包含多个安装步骤，每步最多 600 秒，调用时应允许总计至少 1800 秒。

发布到 B站需要本地 biliup 程序：发布与 `--dry-run` 只做只读检查，缺失返回 `ENV-007`；用 `opub --repair-env --with-bilibili` 显式安装，普通修复不安装。B站子进程限时：查询 60 秒、扫码登录 360 秒、上传 3600 秒；上传超时结果未确认且不可自动重试，应引导用户到平台人工核对。

## 已验证平台（7个）

| 平台标识 | 名称 | 视频 | 图文 | 说明 |
| --- | --- | --- | --- | --- |
| `douyin` | 抖音 | ✅ | ✅ | |
| `xiaohongshu` | 小红书 | ✅ | ✅ | 浏览器自动化 |
| `kuaishou` | 快手 | ✅ | ✅ | 浏览器自动化 |
| `bilibili` | B站 | ✅ | ❌ | 需先 `opub --repair-env --with-bilibili` 安装 biliup，自动抓取BV号 |
| `tencent` | 视频号 | ✅ | ❌ | |
| `baijiahao` | 百家号 | ✅ | ❌ | 浏览器自动化 |
| `weibo` | 微博 | ✅ | ❌ | 单账号自动发现 |

## 触发场景

当用户表达下面任一意图时使用本 skill：

- 发布视频、上传视频、一键发布、多平台发布、图文发布
- 发布到抖音、小红书、快手、微博、B站、视频号、百家号
- 配置发布平台、账号、cookie、登录校验、扫码登录
- 排查 `opub`、Chromium 或浏览器驱动问题
- 查看发布历史、任务状态、原记录链接及恢复条件

## 调用

`opub` 的新任务通过命令行参数接收全部发布信息；恢复已有任务使用 `--resume RUN_ID`：

```bash
# 视频发布(必填:--platforms + --video)
opub --platforms douyin,weibo --video videos/demo.mp4 --title "标题" --tags "标签1,标签2"

# 图文发布
opub --platforms xiaohongshu --note --images img1.jpg,img2.jpg --title "标题"

# 图文转视频(视频号/百家号等不支持图文的平台)
opub --platforms tencent --note --images img1.jpg --convert-to-video --video-duration 5

# 定时 / 从目录第 2 个视频开始 / 强制重新生成
opub --platforms weibo --video videos/ --title "标题" --schedule "2027-01-01 12:00" --start-from 2 --force

# 有头模式排查(发布默认无头不弹窗;扫码登录始终显示窗口)
opub --platforms douyin --video videos/demo.mp4 --title "标题" --no-headless

opub --version                        # 查看已安装版本
opub --help                           # 全部参数说明
```

参数说明:**素材路径(`--video`/`--images`)、标题、描述、话题标签(`--tags`)、目标平台是每次发布的输入,执行前必须逐项向用户确认,不要自行检索文件系统挑素材,也不要替用户编写标题/描述/话题**。仅当用户明确表示留空自动生成时,`--title`/`--desc` 才可留空走自动生成(需视频同名 JSON 或 ZHIPU_API_KEY),生成失败报 CFG-001,此时向用户报告错误并请用户提供 `--title` 重试,不要自行编一个标题;`--schedule` 指定后本次为定时发布。每个平台只自动发现一个规范账号文件；未发现账号时，发布流程会引导扫码并写入对应上传器目录的 `account.json`。**启用平台若无账号文件,发布时会自动弹出浏览器扫码登录**,登录完成后继续发布,不需要提前单独登录。浏览器平台每个素材在单页会话内完成登录与上传：发布默认无头,需要扫码时自动弹出独立的可见登录窗口,扫码后带新登录状态重启无头会话继续上传,结束后关闭；不同平台或账号分别管理会话。发布过程默认无头(不弹浏览器窗口),含发布前的登录状态检查;仅排查平台风控或元素定位问题时才加 `--no-headless` 回到有头模式,普通发布不要加。

同一份素材的全部启用平台默认并发发布，无需额外参数。各平台在自己的流程中调用现有登录校验；需要扫码时分别打开登录窗口，不统一排队，一个平台等待扫码不阻塞其他平台。目录中的多份素材仍按顺序处理，每份素材的全部平台结束后再开始下一份。

### 预检与恢复

对已确认的发布输入添加 `--dry-run --output json` 可先验证输入与环境，无需许可；不会登录、发布、自动生成文案或转换图片。成功时从 `planned` 读取计划，不能将其描述为发布成功。实际发布前会先解析全部素材的标题；定时至少提前两小时，当前 B站不支持定时。

实际发布后保存 `run_id`。用户要求继续失败或中断的任务时，使用 `opub --resume RUN_ID --output json`，不要重跑原始普通发布命令，也不要附加标题、平台、素材等新参数。恢复沿用已解析参数与账号文件路径；`reused: true` 是已有成功结果，不是本次新提交。尚未执行或明确未提交的项有原账号身份记录时可继续。上传前核验当前实际账号：同账号正常刷新可以恢复，换号或身份无法核验返回 `AUTH-003`，本次未上传，恢复原账号后再次 resume，不自动重新扫码。旧记录或未绑定原身份返回 `RUN-006`，不登录、不提交、不回填当前账号，也不自动创建新任务绕过；TikTok 当前缺少可核验的稳定身份来源，未绑定条目不能恢复。`RUN-004` 仍表示结果未确认，先核对平台作品，不自动重发；成功旧记录仍复用。`RUN-003` 表示素材改变/缺失或记录无效，`RUN-005` 表示记录读写失败。只有用户确定需要新发布或变更参数时才创建新任务。

`--start-from` 仅选择新任务的目录起始序号，不是平台级恢复；不要用它跳过部分平台的成功记录。发布记录在数据目录的 `publish-history.sqlite3`，不要删除或覆盖记录来绕过重复提交保护。


视频号与快手只在本次完整文案和有限上传/提交时间范围内找到唯一作品时返回链接；列表延迟、未完整取证的分页列表、审核中、字段缺失或多候选时保持空链接。`result_url` 表示已归因的作品地址，不代表已经独立验证公开播放；不得为补链接重新投稿。

### 历史只读查询与核对

用户要查看已有任务时，直接查询，不先运行许可、环境修复、登录或恢复：

```bash
opub --history --output json
opub --history --limit 5 --output json
opub --history RUN_ID --output json
```

列表默认 20 个任务，`--limit` 范围 1–200，只适用于列表。查询只读 `~/.opub/publish-history.sqlite3`，不读取当前素材或账号文件，不创建目录 / 数据库、不迁移、不补写身份、不投稿或核销历史；旧版 v1 无账号表也可读。素材已删除 / 改动时仍显示保存的路径、文案和指纹。数据库缺失时列表为空；任务缺失 / 损坏返回 `RUN-003`，读取失败、锁、热日志或 WAL 返回 `RUN-005`，保留数据库和日志，等待原发布进程结束，不删除或强制恢复。查询不能混入发布、扫码、环境修复、激活或 `--resume` 参数。

JSON `mode` 为 `history_list` / `history_detail`，数据在 `history`，`results: []` 和顶层 `summary` 均为 0，不是新发布结果。有效查询退出 0，即使旧任务失败或被阻断；查询 / 参数错误退出 2。列表按 `order: insertion_desc` 排序，`created_at: null` 表示未记录创建时间，不从 UUID 或文件时间猜测。每个任务的 `states` / `resume` 分别统计原状态和恢复决策。

详情的 `items[].platforms[]` 中，`identity_status: bound` 仅表示原身份已绑定，当前账号未核验；`resume.status` 按以下顺序解释：`reuse_success` 复用成功不再投稿；`blocked_unknown` / RUN-004 等待原进程或到原账号后台核对，不重发；`blocked_identity` / RUN-006 不用当前账号补证或自动创建新任务绕过；`requires_checks` 仅满足记录层条件，实际恢复仍检查素材、计划、许可、环境及当前账号，并由原子领取保护提交。

`evidence.source: local_history` 表明仅为旧记录；`submission: recorded_success` 是记录成功，`attribution: recorded_link` 是经过域名 / 作品路径检查的原成功链接，不代表本次重新归因。`public_access` 始终为 `not_checked`，不能报告公开播放已验证。缺失 / 无效 / 失败条目链接为 null，不从作品 ID 拼接。输出只含已知结果字段，不输出原身份摘要或额外凭据字段。

核对步骤：先等待仍在运行的发布结束；使用原账号进入平台后台，对比原完整标题、描述、标签、素材和计划时间；分别确认提交、作品归因、公开访问 / 播放。列表延迟、多候选或字段不全继续保留未决。后续任务成功不能自动核销旧未知记录，不为补链接重投，不删除或改写历史来绕过保护。

## 付费许可

`opub 0.x 创始版`售价 ¥9.90，通过 Agent 内的支付宝付款请求购买，付款核验后自动激活当前设备。一次购买绑定一台设备，无订阅；已安装的 `0.x` 版本可永久离线验签使用。许可不迁移、不解绑、不提供换机重置，新电脑重新购买，未来大版本需要单独购买。opub 自身不设账号。公开 Python 包是诚实用户门禁，属于非强 DRM。

### 支付依赖检查

先检查本机许可；只有需要购买或继续付款时才检查支付依赖。有效许可、只读历史、`--dry-run` 和环境修复不以支付技能或钱包为前提。

| 依赖 | 用途与检查方式 |
| --- | --- |
| `alipay-payment-skill` | 支付宝官方支付技能；必须能在当前 Agent 会话中发现并加载，用其 `references/402-payment.md` 处理 opub 的账单 |
| `alipay-authenticate-wallet` | 支付宝官方钱包技能；一并安装，在用户明确要求钱包开通/授权或支付命令明确要求独立钱包流程时才调用 |
| `alipay-bot` | 官方买方支付 CLI；在 Agent 实际执行命令的环境中检查 PATH（macOS/Linux 用 `command -v alipay-bot`，Windows 用 `Get-Command alipay-bot`），再运行 `alipay-bot --version` |

缺少技能时，通过宿主支持的技能安装方式，从[支付宝官方仓库](https://github.com/alipay/payment-skills)导入上述两个同名目录，保留完整的 `SKILL.md`、`references/` 和 `.signature/`。WorkBuddy 的用户级安装位置为 `~/.workbuddy/skills/<技能名>/`；不要安装到其他 Agent 的目录。安装后刷新技能或开启新会话，确认宿主能发现并加载，不能仅凭磁盘存在文件就宣称可用。

技能可加载但 CLI 缺失时，读取官方技能的 `references/cli-setup.md`，按其指定 npm 包版本和完整性校验步骤安装；缺少 Node.js/npm 时先补齐该安装前提。`pip install opub` 和 `opub --repair-env` 不会安装这些支付依赖。安装失败或宿主无法加载时，保留原发布输入和购买记录，明确报告缺失依赖及恢复步骤，停止购买后的发布流程，不把“没有支付能力”当作免付费。

支付前加载官方支付技能并遵循其流程；不要自行拼装支付命令，也不要把 `check-wallet` 作为每次付款的前置步骤。钱包授权和本人付款确认由官方流程处理；已有授权不重复申请。

### 购买与恢复

Agent 先保留已确认的发布输入，并运行 `opub --license-status`。尚未激活时运行：

```bash
opub --activate --output json
```

读取 JSON 的 `mode: activation` 和 `activation.status`：

- `payment_required`：向用户说明商品、¥9.90 价格和单设备买断规则，取得本次购买确认并完成支付依赖检查后，调用支付宝官方支付技能 `alipay-payment-skill`。原样使用 `payment_needed_file` 中的账单和 `request.url`、`request.method`、`request.body`，不改写账单，也不重新生成订单。支付技能负责钱包授权、本人付款确认和待付款状态查询。付款完成后重试同一激活命令，直到客户端返回 `licensed`；支付工具显示成功不等于本机已激活。
- `pending_confirmation`：已验付，正在确认交付。重试同一激活命令恢复；不得再次发起付款。
- `licensed`：许可证已经在本机验签并安装。确认 `opub --license-status` 成功，再自动继续同一个发布任务，不重复询问素材、文案或平台。
- `unavailable` 或 `LIC-xxx`：保留原购买记录，按错误建议恢复。不得把网络错误当成未付款，也不得删除本地购买状态来重复下单。

用户亲自在支付宝确认付款。不得索取验证码、支付密码或账号密码，不以用户口头“已付款”代替官方验付。不得读取、复制或展示 `activation-purchase.json` 中的领取凭据，也不展示设备哈希、支付凭证和签名许可证原文。

许可检查未成功前，不得执行实际发布、改用底层上传器、修改许可状态，或用 `--dry-run` 冒充已发布。支付依赖缺失不允许改用个人收款码、手工订单号验付、微信或其他未接入的付款渠道。若官方提示“买家和卖家不能相同”，停止同账号重试，说明需由另一位真实买家本人付款；保留原订单，不擅自换绑钱包或新建订单。

激活只在需要联网购买或恢复时联网；安装后的许可验证保持离线。

许可错误统一输出 `[opub] LIC-xxx: <描述>。建议: <动作>`。常见错误及建议：

| 错误码 | 含义 | 建议 |
| --- | --- | --- |
| `LIC-001` | 尚未激活 | 执行激活命令 |
| `LIC-002` | 损坏签名 | 联系支持并提供错误码 |
| `LIC-003` | 许可属于其他设备 | 新电脑重新购买 |
| `LIC-004` | 稳定设备标识不可用 | 联系支持并提供错误码 |
| `LIC-011` | 服务不可用 | 稍后重试 |
| `LIC-013` | 激活码无效 | 检查激活码后重新激活 |
| `LIC-014` | 激活码已绑定其他设备 | 当前电脑重新购买 |
| `LIC-015` | 当前客户端版本不适用 | 升级或切换到 opub 0.x 后重试 |

退出码 `13`（`exit 13`）表示当前尚未完成激活；待付款和待确认交付通过 `activation.status` 区分。显示 `LIC-xxx` 时按表中建议处理。

## Agent 用户反馈

本技能只供 Agent 使用。Agent 执行发布时，用户可见反馈仅限以下三类：

1. **发布环境状态**：正在检查、已就绪，或环境异常的简短结论。
2. **发布开始**：发布已启动，可包含目标平台和素材数量。
3. **发布结果**：各平台结果（成功或失败）、错误码、结果链接和总体计数。

首次付费激活另行展示商品、价格、单设备规则，并请求本人确认付款；待交付时仅说明恢复状态。

执行 `opub ...` 时，必须将 stdout 和 stderr 重定向到 Agent 内部临时日志，禁止向用户展示或转述原始命令输出。Agent 只可在内部读取日志以判断退出码并提取最终结果，不得把内部日志转化为过程消息。

发布运行期间不发送发布进度，不转述依赖安装、登录过程、浏览器操作、调试信息或异常堆栈。浏览器登录交互由浏览器界面自行提示，Agent 不追加扫码或操作提醒。失败时只反馈稳定错误码、简短原因和最终建议。

## 读取结果

### 首选 JSON 格式

Agent 发布时优先添加 `--output json`，将 stdout 保存为结果 JSON，将 stderr 单独保存为内部诊断日志。stdout 只有一份文档，字段为 `schema_version`（当前 1）、`mode`、`run_id`、`planned`、`exit_code`、`summary`、`results`、`errors`。文本输出仍可使用，下文格式保持兼容；`--help` 与 `--version` 始终为文本。

`results` 每项含 `material`（视频路径或图文图片路径数组）、`content_type`、`platform`、`success`、`message`、`error_code`、`result_url`、`result_id`、`safe_to_retry`、`reused`、`action`。成功但 URL 为 null 仍是成功。仅当 `safe_to_retry` 明确为 true 才可自动重试，缺省 false。`errors` 每项含 `error_code`、`message`、`action`，用于配置、环境、许可及运行异常。

`summary` 的 `success`/`failed` 只统计已记录的平台结果；判断整次任务必须同时查看 `exit_code` 和 `errors`。中途失败仍保留此前结果，中断返回 130 和 `RUN-002`，重试前先核实平台作品状态。

### 退出码

| 退出码 | 含义 | Agent 下一步 |
| --- | --- | --- |
| 0 | 执行成功 | 先看 mode：dry_run 仅汇报预检通过；publish/resume 从结果提取链接，并区分 reused |
| 1 | 部分平台成功、部分失败 | 读"发布结果"汇总，向用户汇报成败明细 |
| 2 | 全部平台发布失败 | 读各平台 [PUB-xxx] 错误码，按建议动作处理 |
| 10 | 配置错误 | 按 stderr 的 CFG-xxx 建议修正命令行参数（CFG-001 标题为空时补 `--title`） |
| 11 | 环境错误 | 按 stderr 的 ENV-xxx 建议执行安装命令后重试 |
| 12 | 账号未登录且扫码未完成 | 在发布结果中反馈 AUTH-xxx，不追加扫码提示 |

### 错误输出格式

所有流程级错误输出到 stderr，格式固定：

```
[opub] <错误码>: <描述>。建议: <可执行的动作>
```

错误码体系：`CFG-xxx` 配置、`ENV-xxx` 环境、`AUTH-xxx` 登录、`PUB-<platform>` 平台发布失败（出现在"发布结果"汇总行中）、`RUN-xxx` 运行时异常（意外错误，退出码 2）。

登录检查遇到 `NET-001`（网络失败或超时）、`PAGE-001`（页面无法识别）、`ENV-006`（本机环境或账号文件不可用）时，不得当作账号失效引导扫码或自动重试发布，按 `action` 处理。仅缺少账号或有明确登录失效证据才进入扫码流程。全部平台因这些检查失败时退出码为 2，部分成功时为 1。

`ENV-007` 表示启用 B站但本地 biliup 程序缺失或不可执行：按 `action` 运行 `opub --repair-env --with-bilibili` 安装后重试。

### 结果汇总格式

发布结束打印稳定格式的汇总（stdout）：

```
========== 发布结果 ==========
抖音: ✅ 成功 https://www.douyin.com/video/123
B站: ✅ 成功
微博: ❌ 失败 [PUB-weibo]: 上传超时

========== 总体发布汇总 ==========
成功: 2 次
失败: 1 次
```

成功平台的结果链接显示在对应平台的汇总行中。Agent 从发布结果汇总中提取结果链接并反馈给用户，仅在汇总行存在 URL 时反馈链接。成功但没有 URL 表示发布成功但暂时无法抓取链接，不得视为发布失败；不创建或依赖 Excel 结果文件。

## 环境排查（防御性说明）

Agent 的运行沙箱可能自带**独立 Python 环境**（与项目 venv、系统 Python 均不同），且 `python`、`pip`、`opub` 三者在 PATH 中可能解析到**不同的解释器**——用 `python -c "import xxx"` 诊断得到的结果可能来自与 `opub` 实际运行不同的环境。排查或修复依赖时遵守：

1. **统一用 `python -m pip ...` 而不是裸 `pip`**，确保 pip 操作的就是当前 `python` 的环境。
2. **诊断与修复必须用同一个解释器**：修复前先运行 `python -c "import opub, sys; print(sys.executable)"` 确认该环境里 opub 可导入；若 `pip show` 说已安装而 `python -c "import ..."` 报 ModuleNotFoundError，说明两者不是同一环境，先定位 opub 实际所在的解释器再操作。
3. **多平台同时报同一非登录类错误时，优先怀疑依赖损坏而不是引导用户扫码**。典型症状：发布时报 `ENV-006`，内部诊断为 `module 'greenlet' has no attribute 'greenlet'`——greenlet 安装不完整，残缺的包目录会被 Python 当作 namespace package（导入成功但属性缺失），而残留的 dist-info 元数据会让 pip 误判为已装好、重装 opub 也不会补上。
4. **修复依赖损坏**：删除 site-packages 下残缺的包目录及其 `*.dist-info`（dist-info 内缺少 METADATA/RECORD 即为残骸），再 `python -m pip install --force-reinstall --no-deps <包名>` 重装，最后用 `opub --version` 验证。

## Agent 注意事项

- **发布输入必须来自用户**:视频/图片路径、标题、描述、话题标签在执行前逐项向用户确认,不要自行搜索目录选文件、不要替用户编造文案。仅当用户明确授权"留空自动生成"时,才可留空 `--title`/`--desc` 走自动生成。
- **工具超时必须 >= 360 秒**:平台未登录时 opub 会打开浏览器阻塞等待扫码(最长约 5 分钟)。若工具默认超时(如 120 秒)先到期,进程被杀、浏览器一并关闭,登录半途而废且无任何日志。调用前设置足够长的超时,或引导用户先完成一次登录。
- 不要先单独校验登录后再要求用户二次确认发布。
- 发布运行期间不要额外展示二维码、转述登录过程或提示扫码；登录交互由弹出的浏览器界面负责。
- 本项目文档中文优先，不维护国际化文案。
