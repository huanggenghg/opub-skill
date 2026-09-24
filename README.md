# opub Skill

opub 是面向 AI Agent 的多平台内容发布技能。用户用自然语言提供素材、平台和文案，Agent 按 [SKILL.md](SKILL.md) 完成环境检查、安装、许可处理、发布和结构化结果读取。

支持抖音、小红书、快手、Bilibili、视频号、百家号和微博。浏览器、账号 Cookie、媒体文件及发布历史均保存在用户设备上。

## 安装运行时

opub 0.9.0 只提供经过编译的 Python wheel，不提供源码包：

```bash
python -m pip install --only-binary=:all: "opub==0.9.0"
opub --repair-env
```

支持 CPython 3.11、3.12、3.13，以及 macOS arm64/x86_64、Windows x86_64、Linux x86_64。没有匹配 wheel 时不要移除 `--only-binary`，请改用受支持的 Python 和系统组合。

完整的 Agent 行为、发布参数、错误码、许可流程和 JSON 结果协议均在 [SKILL.md](SKILL.md) 中。

## 发行边界

- 本仓库公开发布 Skill、安装协议和用户文档。
- opub 0.9.0 运行时通过 PyPI 分发编译 wheel，核心运行源码不在本仓库中。
- `huanggenghg/opub` 保留 0.8.21 及更早版本的历史开源代码和 MIT 权利。
- 编译会提高直接读取和修改运行时代码的成本，但不承诺阻止专业逆向。

产品信息和购买入口：<https://opub.cn>

## 许可证

本仓库的 Skill 和文档采用 [MIT License](LICENSE)。该许可证不适用于 PyPI 中的 opub 0.9.0 私有运行时。
