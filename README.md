# opub Skill

opub 是面向 AI Agent 的多平台内容发布技能。用户用自然语言提供素材、平台和文案，Agent 按 [SKILL.md](SKILL.md) 完成环境检查、安装、许可处理、发布和结构化结果读取。

支持抖音、小红书、快手、Bilibili、视频号、百家号和微博。浏览器、账号 Cookie、媒体文件及发布历史均保存在用户设备上。

## 安装运行时

opub 0.9.16 只提供经过编译的 Python wheel，不提供源码包：

```bash
python -m pip install --only-binary=:all: "opub==0.9.16"
opub --repair-env
```

支持 CPython 3.11、3.12、3.13，以及 macOS arm64/x86_64、Windows x86_64、Linux x86_64。没有匹配 wheel 时不要移除 `--only-binary`，请改用受支持的 Python 和系统组合。

完整的 Agent 行为、发布参数、错误码、许可流程和 JSON 结果协议均在 [SKILL.md](SKILL.md) 中。

同一份素材的全部启用平台默认并发发布，各平台分别校验登录与扫码，无需额外参数。目录中的多份素材仍按顺序处理。

无需许可、素材或浏览器即可只读查看原发布任务：`opub --history` 列出最近任务，`opub --history RUN_ID --output json` 返回原任务详情与恢复条件。未知提交仍需核对原账号后台，不自动重投。

## 第一次发布

先按 [首次发布教程](docs/first-publish.md) 检查本机环境，用自己的素材做免费预检，再确认真实发布。首次建议选择两个平时常用的平台。

0.x 创始版 ¥9.90，首次激活绑定一台设备；许可覆盖 0.x，已安装的 0.x 版本可永久离线使用。许可不迁移、不解绑、不提供换机重置，未来大版本单独购买。完整费用与激活说明见 [SKILL.md](SKILL.md#付费许可)。

首次购买所需的支付宝官方技能 `alipay-payment-skill`、`alipay-authenticate-wallet` 已随本技能提供（见 `bundled/`）。本技能须按完整目录安装，不要只复制 `SKILL.md`；否则不包含 `bundled/` 和 `install.py`。安装本技能后，Agent 在首次购买时会运行一次 `python install.py`，把两个同级技能放到宿主技能目录；用户不需要单独导入。需要预装 `alipay-bot` CLI 时运行 `python install.py --install-cli`，脚本按官方锁定的 npm 版本和 integrity 校验安装；失败时由支付技能按官方 `references/cli-setup.md` 处理。已有有效许可无需支付能力。

## 发行边界

- 本仓库公开发布 Skill、安装协议和用户文档。
- opub 0.9.16 运行时通过 PyPI 分发编译 wheel，核心运行源码不在本仓库中。
- `huanggenghg/opub` 保留 0.8.21 及更早版本的历史开源代码和 MIT 权利。
- 编译会提高直接读取和修改运行时代码的成本，但不承诺阻止专业逆向。

产品信息与完整技能：<https://opub.cn>。购买由本地 Agent 发起支付宝付款请求，经本人确认付款后自动激活。

## 许可证

本仓库的 Skill 和文档采用 [MIT License](LICENSE)。该许可证不适用于 PyPI 中的 opub 0.9.16 私有运行时。`bundled/` 下的支付宝官方技能按 Apache License 2.0 分发，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
