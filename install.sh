#!/usr/bin/env bash
# 自体心理学督导技能 - 安装脚本 (macOS / Linux)
set -e

SKILL_NAME="self-psychology-supervision"
TARGET_DIR="${HOME}/.claude/skills/${SKILL_NAME}"

echo "=== 自体心理学督导技能 安装 ==="
echo "目标目录: ${TARGET_DIR}"

if [ -d "${TARGET_DIR}" ]; then
    echo ""
    echo "⚠️  目标目录已存在。"
    read -p "是否覆盖？(y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消。"
        exit 1
    fi
    rm -rf "${TARGET_DIR}"
fi

mkdir -p "$(dirname "${TARGET_DIR}")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -R "${SCRIPT_DIR}" "${TARGET_DIR}"

# 清理不需要的安装产物
rm -f "${TARGET_DIR}/install.sh" "${TARGET_DIR}/install.ps1"

echo ""
echo "✅ 安装完成: ${TARGET_DIR}"
echo ""
echo "下一步：重启你的 Claude Code / 兼容客户端，然后直接说："
echo "    督导一下这个案例"
