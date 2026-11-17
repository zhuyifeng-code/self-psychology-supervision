# 在 Agent Harness 中从 GitHub 安装本技能

适用于 DeepSeek Harness、Codex CLI / Codex 桌面版，以及任何兼容 `~/.claude/skills`、`~/.codex/skills` 目录约定、支持 `SKILL.md` 的 Agent 客户端。

本仓库**根目录本身就是一个合法的 skill 目录**（`SKILL.md` + `assets/prompts/`），因此可以直接被安装器识别，不需要指定子路径。

---

## 一、最省事的做法：让 Agent 自己装

在 harness 的对话框里直接说：

```
从 GitHub 安装这个 skill：
https://github.com/zhuyifeng-code/self-psychology-supervision
```

Agent 会调用它的 skill-installer 完成安装。装完**下一轮对话**即可生效（当前对话不会热加载）。

---

## 二、Codex 自带安装器（推荐，可复现）

Codex 内置 `skill-installer`，脚本位置：

```
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py
```

在仓库根目录执行：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhuyifeng-code/self-psychology-supervision \
  --path .
```

Windows PowerShell：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo zhuyifeng-code/self-psychology-supervision `
  --path .
```

常用参数：

| 参数 | 说明 |
|---|---|
| `--ref main` | 指定分支 / tag / commit |
| `--dest <path>` | 装到非默认目录 |
| `--method download` | 强制走 zip 下载（默认） |
| `--method git` | 强制走 git sparse checkout |

安装目标默认是 `$CODEX_HOME/skills/<skill-name>`，即 `~/.codex/skills/self-psychology-supervision`。

> 脚本在目录已存在时会**直接中止**，不会覆盖。想重装先手动删掉目标目录。

---

## 三、纯 git clone（任何 harness 通用）

```bash
git clone https://github.com/zhuyifeng-code/self-psychology-supervision.git \
  ~/.codex/skills/self-psychology-supervision
```

要用在 Claude Code，把目标换成 `~/.claude/skills/self-psychology-supervision`：

```bash
git clone https://github.com/zhuyifeng-code/self-psychology-supervision.git \
  ~/.claude/skills/self-psychology-supervision
```

Windows PowerShell：

```powershell
git clone https://github.com/zhuyifeng-code/self-psychology-supervision.git "$env:USERPROFILE\.codex\skills\self-psychology-supervision"
```

后续更新只需 `git pull`：

```bash
git -C ~/.codex/skills/self-psychology-supervision pull
```

---

## 四、网络受限时的手动安装

国内网络下 `raw.githubusercontent.com` 常被阻断（表现为 `HTTP 000` / 连接超时），但 `github.com` 主站和 `codeload.github.com` 通常可达。这时走 zip：

```bash
curl -L -o skill.zip \
  https://codeload.github.com/zhuyifeng-code/self-psychology-supervision/zip/refs/heads/main

unzip -q skill.zip -d /tmp/
mkdir -p ~/.codex/skills
mv /tmp/self-psychology-supervision-main ~/.codex/skills/self-psychology-supervision
```

或者直接把仓库页面上的 **Code → Download ZIP** 下载下来解压，把解压出的文件夹整体放进 `~/.codex/skills/` 并改名为 `self-psychology-supervision`。

如果连 `codeload` 也不通，用 GitHub 反代前缀（任选其一，可用性随时变化）：

```
https://ghfast.top/https://github.com/zhuyifeng-code/self-psychology-supervision/archive/refs/heads/main.zip
https://gh-proxy.com/https://github.com/zhuyifeng-code/self-psychology-supervision/archive/refs/heads/main.zip
```

---

## 五、装完怎么确认

```bash
ls ~/.codex/skills/self-psychology-supervision/
# 应看到：SKILL.md  assets/  README.md  LICENSE  install.sh  install.ps1
```

在 harness 里发一句：

```
督导一下这个案例
```

能自动读取 `assets/prompts/` 下的模板并列出自体心理学督导结构，就说明生效了。若没反应，重启客户端——大多数 harness 只在启动时扫描 skills 目录。

---

## 六、常见问题

**Q：装完完全没反应？**
A：① 确认目录名是 `self-psychology-supervision`；② 确认 `SKILL.md` 在目录**根层**而不是多套了一层（`.../self-psychology-supervision/self-psychology-supervision/SKILL.md` 是错的）；③ 重启客户端。

**Q：Agent 说找不到 SKILL.md？**
A：多套了一层目录，把内层内容上移一层即可。

**Q：想同时给 Codex 和 Claude Code 用？**
A：两边各装一份，或装一份然后在另一侧做目录符号链接。Windows 下用 `mklink /D`（需管理员），macOS/Linux 用 `ln -s`。

**Q：模板文件读不到？**
A：`assets/prompts/` 是技能的一部分，必须随 `SKILL.md` 一起安装，不能只拷 `SKILL.md`。

---

## 七、隐私提醒

案例材料含来访者隐私。使用任何云端模型时材料都会发送至服务商，**请先做去标识化处理**（姓名、地点、单位、可识别细节）。材料如何传输、留存与合规性判断由使用者自行负责；本技能不提供数据安全保证。
