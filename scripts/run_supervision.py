#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
督导分析委托脚本：把组装好的督导提示词发送到 config.json 指定的模型。

用法：
  python3 run_supervision.py --case case.txt [--modules core,technique] \
      [--question "补充的督导疑问"] [--history h1.txt h2.txt h3.txt] \
      [--model 覆盖模型] [--max-tokens 8192] [--out report.md]

参数：
  --case        案例材料文件（txt/md），必填；传 "-" 则读 stdin
  --modules     逗号分隔的模块名：core,technique,dialogue,dream,child,short_term,continuous
                （默认 core）
  --question    用户的督导疑问（可空）
  --history     continuous 模块的历史分析文件，每个 ≤6000 字符，最多取最近 3 个
  --model       覆盖 config.json 中的模型
  --max-tokens  覆盖默认输出上限
  --out         结果写入文件（不传则打印到 stdout）

流程：读取 assets/prompts/supervision_prompt_base.txt 为骨架，
      {context} = 所选模块模板拼接，{query} = 案例全文 + 疑问，
      以 Anthropic /v1/messages 协议发送，返回文本内容。
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(SKILL_DIR, "assets", "prompts")
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")

MODULE_FILES = {
    "core": "supervision_prompt_core.txt",
    "technique": "supervision_prompt_technique.txt",
    "dialogue": "supervision_prompt_dialogue.txt",
    "dream": "supervision_prompt_dream.txt",
    "child": "supervision_prompt_child.txt",
    "short_term": "supervision_prompt_short_term.txt",
    "continuous": "supervision_prompt_continuous.txt",
}
HISTORY_CHAR_LIMIT = 6000
HISTORY_MAX_ROUNDS = 3


def load_config():
    """读取技能目录下的 config.json；缺失时回退到环境变量。

    config.json 优先（形状见 config.example.json）。没有该文件时，
    SUPERVISION_BASE_URL / SUPERVISION_API_KEY / SUPERVISION_MODEL 提供必填项，
    SUPERVISION_MAX_TOKENS / SUPERVISION_TEMPERATURE / SUPERVISION_TIMEOUT 可选覆盖。
    仓库里不提交任何密钥。
    """
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    required = {
        "base_url": os.environ.get("SUPERVISION_BASE_URL", ""),
        "api_key": os.environ.get("SUPERVISION_API_KEY", ""),
        "model": os.environ.get("SUPERVISION_MODEL", ""),
    }
    missing = [f"SUPERVISION_{name.upper()}" for name, value in required.items() if not value]
    if missing:
        sys.exit(
            "缺少模型配置：" + "、".join(missing) + "\n"
            "把 config.example.json 复制成 config.json 填入端点与密钥，"
            "或设置上面的环境变量。详见 README 的「委托外部模型」一节。"
        )
    cfg = dict(required)
    for env_name, key, cast in (
        ("SUPERVISION_MAX_TOKENS", "max_tokens", int),
        ("SUPERVISION_TEMPERATURE", "temperature", float),
        ("SUPERVISION_TIMEOUT", "timeout", int),
    ):
        raw = os.environ.get(env_name)
        if raw:
            cfg[key] = cast(raw)
    return cfg


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


CONTINUE_INSTRUCTION = """
---
【续写任务】以下是你刚刚为同一案例输出的分析，因长度限制在途中被截断：

<<<已有内容开始
{partial}
已有内容结束>>>

请**从中断处接着继续输出剩余部分**：
- 不要重新开头，不要重复已有内容，不要复述已经写过的段落；
- 保持原有的标题层级与格式风格（若中断在某小节中间，直接续写该小节剩余内容）；
- 直到该模块的所有要求全部写完为止。
"""


def build_prompt(modules, case_text, question, history_files, extra_context=None, continue_from=None):
    base = read_text(os.path.join(PROMPTS_DIR, "supervision_prompt_base.txt"))

    context_parts = []
    if extra_context:
        context_parts.append(read_text(extra_context))
    for m in modules:
        if m not in MODULE_FILES:
            sys.exit(f"错误：未知模块 '{m}'，可用：{', '.join(MODULE_FILES)}")
        tpl = read_text(os.path.join(PROMPTS_DIR, MODULE_FILES[m]))
        if m == "continuous" and history_files:
            files = history_files[-HISTORY_MAX_ROUNDS:]
            texts = []
            for i, hf in enumerate(files, 1):
                t = read_text(hf)
                if len(t) > HISTORY_CHAR_LIMIT:
                    t = t[:HISTORY_CHAR_LIMIT] + "……（超出长度已截断）"
                texts.append(f"【第 {i} 次分析】\n{t}")
            tpl = tpl.replace("{history_count}", str(len(files)))
            tpl = tpl.replace("{history_text}", "\n\n".join(texts))
        else:
            tpl = tpl.replace("{history_count}", "0").replace("{history_text}", "（无历史分析）")
        context_parts.append(tpl)

    query = case_text.strip()
    if question:
        query += f"\n\n【督导疑问】\n{question.strip()}"

    prompt = base.replace("{context}", "\n\n".join(context_parts)).replace("{query}", query)
    if continue_from:
        prompt += CONTINUE_INSTRUCTION.replace("{partial}", read_text(continue_from))
    return prompt


def call_model(prompt, cfg, model_override, max_tokens_override):
    payload = {
        "model": model_override or cfg["model"],
        "max_tokens": max_tokens_override or cfg.get("max_tokens", 32000),
        "temperature": cfg.get("temperature", 0.7),
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        cfg["base_url"].rstrip("/") + "/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": cfg["api_key"],
            "Authorization": "Bearer " + cfg["api_key"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=cfg.get("timeout", 600)) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"模型调用失败 HTTP {e.code}: {body}")
    except Exception as e:
        sys.exit(f"模型调用失败: {e}")

    # 拼接所有 text 块（thinking 块不进报告）
    chunks = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    text = "\n".join(c for c in chunks if c).strip()
    if not text:
        sys.exit("模型未返回文本内容（可能被 max_tokens 截断在 thinking 阶段，可调大 --max-tokens）")
    usage = data.get("usage", {})
    print(f"[meta] model={data.get('model')} in={usage.get('input_tokens')} out={usage.get('output_tokens')}",
          file=sys.stderr)
    return text


def main():
    ap = argparse.ArgumentParser(description="督导分析委托脚本")
    ap.add_argument("--case", required=True, help="案例文件路径，'-' 读 stdin")
    ap.add_argument("--modules", default="core", help="逗号分隔模块名")
    ap.add_argument("--question", default="", help="督导疑问")
    ap.add_argument("--history", nargs="*", default=[], help="continuous 历史分析文件（按时间序）")
    ap.add_argument("--extra-context-file", default=None, help="额外上下文模板文件（追加到 {context} 最前）")
    ap.add_argument("--with-theory", action="store_true", help="把 references/theory.md 注入上下文（该文件不存在时忽略）")
    ap.add_argument("--dry-run", action="store_true", help="只组装提示词并打印统计，不发送请求")
    ap.add_argument("--continue-from", default=None, help="已输出文件：从中断处续写")
    ap.add_argument("--model", default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    case_text = sys.stdin.read() if args.case == "-" else read_text(args.case)
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    if not modules and not args.extra_context_file:
        sys.exit("错误：--modules 与 --extra-context-file 至少提供一个")
    if "continuous" in modules and not args.history:
        sys.exit("错误：continuous 模块需要 --history 提供历史分析文件")

    extra = args.extra_context_file
    if args.with_theory:
        theory_path = os.path.join(SKILL_DIR, "references", "theory.md")
        if not os.path.exists(theory_path):
            print("[warn] 本技能没有 references/theory.md，已忽略 --with-theory", file=sys.stderr)
        elif extra:
            merged = os.path.join(SKILL_DIR, "_theory_plus_extra.txt")
            with open(merged, "w", encoding="utf-8") as f:
                f.write(read_text(theory_path) + "\n\n" + read_text(extra))
            extra = merged
        else:
            extra = theory_path
    prompt = build_prompt(modules, case_text, args.question, args.history, extra, args.continue_from)

    if args.dry_run:
        config_note = "未配置"
        try:
            cfg = load_config()
            config_note = f"{cfg.get('base_url')} / {args.model or cfg.get('model')}"
        except SystemExit as error:
            config_note = f"未配置（{error}）"
        print(f"[dry-run] 模块: {','.join(modules)}", file=sys.stderr)
        print(f"[dry-run] 目标: {config_note}", file=sys.stderr)
        print(f"[dry-run] 案例 {len(case_text)} 字 | 提示词 {len(prompt)} 字", file=sys.stderr)
        print("[dry-run] 未发送任何请求", file=sys.stderr)
        return

    text = call_model(prompt, load_config(), args.model, args.max_tokens)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"已写入 {args.out}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
