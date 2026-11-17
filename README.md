# 自体心理学督导技能 · Self Psychology Supervision Skill

> 把科胡特（Kohut）自体心理学的案例督导方法论，做成 AI 可直接执行的结构化技能包。

面向心理咨询师、督导、心理学研究生。提交一份案例报告，产出结构化的专业督导报告——包含个案概念化、自体状态评估、自体客体移情评估、Lichtenberg 十原则技术评估、逐字稿对话分析、梦的分析等模块。

## 这是什么

一份 **提示词工程资产**，不是软件。核心是 `assets/prompts/` 下 8 个经过临床检验的模块化提示词，配一个 `SKILL.md` 说明如何组合使用。

理论框架：
- **科胡特自体心理学**（《自体的分析》1971、《自体的重建》1977）
- **Lichtenberg / Lachmann / Fosshage 十原则**（《临床交流》1992）
- **Lichtenberg《Craft and Spirit》**（2005）逐章展开的技术维度

## 包含哪些模块

| 模块 | 用途 |
|---|---|
| **核心分析** | 个案信息评估（7 项）+ 自体状态评估 + 自体客体移情评估 |
| **技术评估** | 十原则逐条：证据摘录 → 评级 → 红旗 → 改进方向 → 可念话术 → 督导意义 |
| **对话分析** | 逐字稿逐句分析，每条四段式 |
| **梦的分析** | 组织模型视角的梦工作 |
| **短程咨询** | 短程适用性评估 |
| **儿童青少年** | 来访者 <18 岁的附加评估 |
| **连续分析** | 同一案例多次督导的进展追踪 |

## 安装

### 方式零：Agent Harness 从 GitHub 直接装（最省事）

在 DeepSeek Harness / Codex / Claude Code 的对话框里直接说：

```
从 GitHub 安装这个 skill：
https://github.com/zhuyifeng-code/self-psychology-supervision
```

Agent 会调用内置的 skill-installer 完成安装，**下一轮对话生效**。

本仓库根目录本身就是合法的 skill 目录（`SKILL.md` + `assets/prompts/`），不需要指定子路径。Codex 安装器命令：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhuyifeng-code/self-psychology-supervision --path .
```

网络受限、手动安装、装完验证、常见问题，见 **[INSTALL_HARNESS.md](INSTALL_HARNESS.md)**。

### 方式一：Claude Code / 兼容客户端（含 DeepSeek 接入）

```bash
# 克隆到 skills 目录
git clone https://github.com/zhuyifeng-code/self-psychology-supervision.git \
  ~/.claude/skills/self-psychology-supervision
```

**Windows（PowerShell）：**
```powershell
git clone https://github.com/zhuyifeng-code/self-psychology-supervision.git "$env:USERPROFILE\.claude\skills\self-psychology-supervision"
```

装好后重启客户端，技能会自动被识别。

### 方式二：DeepSeek 官方网页 / 任意聊天客户端（无需安装）

1. 打开 `assets/prompts/supervision_prompt_base.txt`
2. 把 `{context}` 替换成你要用的模块内容（如 `supervision_prompt_core.txt` 全文）
3. 把 `{query}` 替换成你的案例报告
4. 整段粘进对话框发送

或者更简单：把 `SKILL.md` + 相关 prompt 文件一起上传给支持文件读取的客户端，让它按 `SKILL.md` 的流程执行。

## 使用

装好之后直接说：

```
督导一下这个案例
```

然后把案例报告粘贴进去或给出文件路径。技能会自动选择模块并产出报告。

也可以指定模块：

```
用技术评估模块督导这个案例，重点看共情沉浸的时机
```

```
这是同一个来访者第三次督导，做连续分析
```

## 输出示例结构

```markdown
# 自体心理学心理咨询督导报告

（本次使用模块：base + core + technique）

## 一、个案信息评估
### 1. 主诉与现病史
- **已有信息**：...
- **评估意义**：...

...（共 7 项）

## 二、自体状态评估
...

## 三、自体客体移情评估
...

## 四、技术评估（Lichtenberg 十原则）
### 原则 1：...
- **证据摘录**：「...」（报告第 X 段）
- **评级**：部分体现
- **红旗**：...
- **改进方向**：...
- **可念话术**：「...」
- **督导意义**：...
```

## 重要声明

- **隐私**：案例材料含来访者隐私。使用云端模型时材料会发送至服务商，**请先做去标识化处理**（姓名、地点、可识别细节）。
- **定位**：本技能产出为**专业督导参考**，不替代真人督导、伦理审查与临床判断。
- **责任**：使用者的临床决策责任始终在自身。

## 许可

MIT License。可自由使用、修改、二次分发。

如果这个技能对你的督导工作有帮助，欢迎 Star 或提交改进。

## 贡献

欢迎 PR 补充：
- 新的督导模块（如团体督导、危机干预评估）
- 不同理论流派的对照视角（Geist 关系性、主体间学派）
- 模板的中英文双语版本

## 作为 DeepSeek Harness 插件安装

本仓库根目录同时是一个 DeepSeek Harness（DSH）bundle：`package.json` 声明 `dsh.bundle.patch`，`cordis.patch.yml` 插入 `skill-self-psychology-supervision` 一行，`index.js` 把本仓库的 `SKILL.md` 注册进会话技能目录（只读文件，不加工具、不改权限、不联网）。

- **从 GitHub 安装**：DSH 里 `plugin_manager` 的 `install_bundle` 目标填 `github:zhuyifeng-code/self-psychology-supervision`；或 **Plugins** 页的安装入口填同一 spec。
- **从本地安装**：**Plugins** > **Add plugin** 选择本目录。
- **不装插件也可以**：把仓库放进 `~/.dsh/skills/`、`~/.agents/skills/` 或项目的 `.agents/skills/`，它就是普通技能，与其他 harness 的装法一致。

