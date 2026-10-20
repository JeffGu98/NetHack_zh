#!/bin/sh
# 一键启动本仓库的简体中文 NetHack。
# 第一次会按 macOS hints 编译并安装；之后直接进入游戏。
# 重新安装（会清空 ~/nethackdir，含存档）: ./play.sh --install

set -e
cd "$(dirname "$0")"

if [ "$(uname -s)" != "Darwin" ]; then
    echo "play.sh 目前只配置了 macOS。其他系统见 sys/unix/NewInstall.unx。" >&2
    exit 1
fi

if [ "$(id -u)" -eq 0 ]; then
    echo "不要用 sudo 运行。用 root 安装后游戏读不到你的 OPTIONS=language:zh。" >&2
    exit 1
fi

if [ -d "$HOME/nethackdir" ] && [ ! -w "$HOME/nethackdir" ]; then
    echo "游戏目录 $HOME/nethackdir 不属于当前用户，所以启动会落到英文。" >&2
    echo "在终端执行下面这一行，输入你的登录密码，然后再运行 ./play.sh：" >&2
    echo "  sudo chown -R \"$(id -un):$(id -gn)\" \"$HOME/nethackdir\" \"$HOME/.nethackrc\"" >&2
    exit 1
fi

do_install=0
if [ "$1" = "--install" ]; then
    do_install=1
    shift
fi

if [ ! -f Makefile ]; then
    (cd sys/unix && sh setup.sh hints/macOS.501)
    do_install=1
fi

if [ ! -x "$HOME/bin/nethack" ] || [ ! -f "$HOME/nethackdir/nhdat" ]; then
    do_install=1
fi

if [ "$do_install" -eq 1 ]; then
    echo "正在安装到 $HOME/nethackdir （该目录会被清空）..."
    make install
fi

rc="$HOME/.nethackrc"
if [ ! -f "$rc" ] && [ -f "$HOME/Library/Preferences/NetHack Defaults" ]; then
    rc="$HOME/Library/Preferences/NetHack Defaults"
elif [ ! -f "$rc" ] && [ -f "$HOME/Library/Preferences/NetHack Defaults.txt" ]; then
    rc="$HOME/Library/Preferences/NetHack Defaults.txt"
fi

if [ -f "$rc" ] && grep -E -q '^OPTIONS=.*(language|lang):' "$rc"; then
    :
else
    printf '%s\n' 'OPTIONS=language:zh' >> "$rc"
    echo "已在 $rc 写入 OPTIONS=language:zh"
fi

exec "$HOME/bin/nethack" "$@"
