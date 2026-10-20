#!/usr/bin/env python3
"""Write dat/locale/zh/cmdhelp and dat/locale/zh/opthelp.

Command keys, option names, and &conditionals stay in English.
Descriptions are Simplified Chinese. Lines stay within 78 columns.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRMAP = {
    "southwest": "西南",
    "northwest": "西北",
    "southeast": "东南",
    "northeast": "东北",
    "west": "西",
    "east": "东",
    "south": "南",
    "north": "北",
}

CMD = {
    "Show the type of an adjacent trap": "查看相邻陷阱的种类",
    "Cancel command (same as ESCape key)": "取消命令（同 Esc）",
    "Search for nearby traps, secret doors, and unseen monsters": "搜索附近的陷阱、秘密门和看不见的怪物",
    "Map level; reveals traps and secret corridors but not secret doors": "绘制本层。显示陷阱和秘密走廊，不显示秘密门",
    "Create a monster by name or class": "按名字或类别创造怪物",
    "View inventory with all items identified": "查看已全部鉴定的背包",
    "List special level locations": "列出特殊层的位置",
    "Teleport between levels": "在楼层之间传送",
    "Wish for something": "许愿",
    "unavailable debugging command": "不可用的调试命令",
    "Shortcut for '#overview': list interesting levels you have visited": "“#overview”的快捷键：列出到过的重要层",
    "Help: synonym for '?'": "帮助，和 ? 相同",
    "Jump: shortcut for '#jump'": "跳跃，即 #jump",
    "Kick: synonym for '^D'": "踢，和 ^D 相同",
    "Loot: shortcut for '#loot'": "搜刮，即 #loot",
    "Start a count; continue with digit(s)": "开始计数，后面跟数字",
    "Name: shortcut for '#name'": "起名，即 #name",
    "Untrap: shortcut for '#untrap'": "解除陷阱，即 #untrap",
    "Apply (use) a tool or break a wand": "使用工具，或折断魔杖",
    "Remove all armor and/or all accessories and/or unwield weapons": "脱下护甲、饰品，或放下武器",
    "Redo the previous command": "重复上一条命令",
    "Close a door": "关门",
    "Call (name) a monster, an individual object, or a type of object": "给怪物、某一件或某一类物品起名",
    "Interrupt: quit the game": "中断并退出游戏",
    "Drop an item": "丢弃一件物品",
    "Drop specific item types": "按种类丢弃",
    "Kick something (usually a door, chest, or box)": "踢东西，通常是门、箱子或盒子",
    "Eat something": "吃东西",
    "Engrave writing on the floor": "在地上刻字",
    "Fire ammunition from quiver": "从箭袋发射",
    "Followed by direction, fight a monster (even if you don't sense it)": "先选方向再攻击，即使没感觉到怪物",
    "Followed by direction, move until you are near something": "先选方向，走到靠近东西为止",
    "Followed by direction, same as control-direction": "先选方向，同按住 Ctrl 的移动",
    "Show your inventory": "显示背包",
    "Inventory specific item types": "按种类查看背包",
    "Followed by direction, move without picking anything up or fighting": "先选方向。移动时不捡东西、不攻击",
    "Followed by direction, move a distance without picking anything up": "先选方向，走出一段距离，不捡东西",
    "Open a door": "开门",
    "Show option settings, possibly change them": "查看并修改选项",
    "Pay your shopping bill": "付店里的账",
    "Put on an accessory (ring, amulet, etc; will work for armor too)": "戴上饰品。也可以穿甲",
    "Toggle through previously displayed game messages": "翻看先前的消息",
    "Quaff (drink) something (potion, water, etc)": "喝药水或水",
    "Select ammunition for quiver (use '#quit' to quit)": "选择箭袋弹药。退出请用 #quit",
    "Read a scroll or spellbook": "读卷轴或魔法书",
    "Remove an accessory (ring, amulet, etc; will work for armor too)": "取下饰品。也可以脱甲",
    "Redraw screen": "重画屏幕",
    "Search all immediately adjacent locations for traps and secret doors": "搜索紧邻的格子有没有陷阱和秘密门",
    "Save the game (and exit; there is no \"save and keep going\")": "保存并退出。不能保存后继续玩",
    "Throw something (choose an item, then a direction--not a target)": "投掷。先选物品，再选方向，不是选目标",
    "Take off one piece of armor (will work for accessories too)": "脱下一件护甲。也可以取下饰品",
    "Teleport around level": "在本层传送",
    "Show version ('#version' shows more information)": "显示版本。#version 显示更多",
    "Show history of game's development": "显示开发历史",
    "Wield a weapon (for dual weapons: 'w' secondary, 'x', 'w' primary, 'X')": "装备武器。双持时 w 副手，x 交换，再 w 主手，X 切换",
    "Wear a piece of armor (will work for accessories too)": "穿上一件护甲。也可以戴饰品",
    "Swap wielded and secondary weapons": "交换主手和副手武器",
    "Toggle two-weapon combat": "切换双持",
    "Show your attributes (shows more in debug or explore mode)": "显示属性。调试或探索模式里信息更多",
    "Zap a wand": "使用魔杖",
    "Zap (cast) a spell": "施放法术",
    "Suspend game; 'fg' (foreground) to resume": "暂停游戏。用 fg 继续",
    "unavailable command: suspend": "不可用的命令：暂停",
    "Go up a staircase": "上楼梯",
    "Go down a staircase": "下楼梯",
    "Show what type of thing a symbol corresponds to": "这个符号代表什么",
    "Give a help message": "显示帮助",
    "Do a shell escape; 'exit' shell to come back": "进入外壳。exit 回到游戏",
    "unavailable command: shell": "不可用的命令：外壳",
    "Show what object types have been discovered": "列出已发现的物品种类",
    "Show discovered types for one class of objects": "列出某一类里已发现的物品",
    "Travel via a shortest-path algorithm to a point on the map": "沿最短路径走到地图上的一点",
    "Rest one move while doing nothing": "休息一回合",
    "Look at what is on the floor": "看地上有什么",
    "Show what type of thing a map symbol on the level corresponds to": "这一层上的这个符号是什么",
    "Pick up things at the current location": "捡起脚下的东西",
    "Toggle the pickup option on/off": "开关自动捡起",
    "Show the weapon(s) currently wielded or readied": "查看当前武器",
    "Show the armor currently worn": "查看穿着的护甲",
    "Show the ring(s) currently worn": "查看戴着的戒指",
    "Show the amulet currently worn": "查看戴着的护身符",
    "Show the tools currently in use": "查看使用中的工具",
    "Show all equipment in use (combination of the ),[,=,\",( commands)": "查看全部装备，相当于 ) [ = \" (",
    "Count your gold": "数金币",
    "List known spells": "列出已学法术",
    "Display map without monsters or objects obstructing the view.": "显示没有怪物和物品挡住的地图",
    "Perform an extended command (use '#?' to list choices)": "执行扩展命令。#? 列出可用项",
    "Show inventory": "显示背包",
    "Move west": "向西移动",
    "Move east": "向东移动",
    "Move northwest": "向西北移动",
    "Move north": "向北移动",
    "Move northeast": "向东北移动",
    "Move southwest": "向西南移动",
    "Move south": "向南移动",
    "Move southeast": "向东南移动",
    "'F' prefix; force fight": "F 前缀：强制攻击",
    "Continue a count": "继续计数",
    "Start or continue a count": "开始或继续计数",
    "'g' movement prefix": "g 移动前缀",
    "'G' movement prefix": "G 移动前缀",
    "Display extended command help (if the platform allows this)": "显示扩展命令帮助",
    "Adjust inventory letters": "调整背包字母",
    "Annotate: supply a name for the current dungeon level": "给当前这一层写注记",
    "Chat: talk to an adjacent creature": "和相邻的生物交谈",
    "Conduct: list voluntary challenges you have maintained": "列出你还保持着的挑战",
    "Dip an object into something": "把一件东西浸入另一件",
    "Enhance: check weapons skills, advance them if eligible": "查看并提高武器技能",
    "Force a lock": "撬锁",
    "Invoke an object's special powers": "发动物品的特殊能力",
    "Jump to a nearby location": "跳到附近一格",
    "Loot a box on the floor": "搜刮地上的箱子",
    "When polymorphed, use a monster's special ability": "变形后使用该怪物的能力",
    "Name a monster, an individual object, or a type of object": "给怪物、某一件或某一类物品起名",
    "Offer a sacrifice to the gods": "向神献祭",
    "Overview: show a summary of the explored dungeon": "查看已探索地城的摘要",
    "Pray to the gods for help": "向神祈祷",
    "Quit (exit without saving)": "不保存并退出",
    "Rub a lamp or a touchstone": "摩擦灯或试金石",
    "Ride: mount or dismount a saddled steed": "骑上或离开鞍马",
    "Sit down": "坐下",
    "Turn undead": "驱散亡灵",
    "Tip: empty a container": "倒空容器",
    "Untrap something (trap, door, or chest)": "解除陷阱、门或箱子上的机关",
    "Print compile time options for this version of NetHack": "显示这个版本的编译选项",
    "Wipe off your face": "擦脸",
    "Switch from normal play to explore mode": "从普通游戏转入探索模式",
}


def cmd_desc(text: str) -> str:
    m = re.match(r"Go (\w+) 1 space", text)
    if m:
        return f"向{DIRMAP[m.group(1)]}走一格"
    m = re.match(r"Go (\w+) until you are on top of something", text)
    if m:
        return f"向{DIRMAP[m.group(1)]}走到踩上东西为止"
    m = re.match(r"Go (\w+) until you are on something", text)
    if m:
        return f"向{DIRMAP[m.group(1)]}走到遇上东西为止"
    m = re.match(r"Go (\w+) until you are near something", text)
    if m:
        return f"向{DIRMAP[m.group(1)]}走到靠近东西为止"
    if text not in CMD:
        raise SystemExit(f"untranslated cmdhelp: {text}")
    return CMD[text]


def columns(s: str) -> int:
    n = 0
    for ch in s:
        n += 2 if ord(ch) > 0x2E80 else 1
    return n


def wrap_note(s: str, limit: int = 78) -> str:
    if columns(s) <= limit and len(s.encode()) < 240:
        return s
    raise SystemExit(f"line too wide ({columns(s)}): {s}")


OPT = {
    "acoustics": "角色能否听见声音",
    "armorstatus": "额外显示穿着的护甲摘要",
    "autodescribe": "说明光标下的地形",
    "autodig": "拿着挖掘工具移动时自动挖",
    "autoopen": "走进门时尝试打开",
    "autopickup": "走过物品时自动捡起",
    "autoquiver": "箭袋空着发射时，自动选一件合适的武器",
    "BIOS": "允许使用 IBM ROM BIOS 调用",
    "blind": "角色永久失明",
    "bones": "允许读取遗骨文件",
    "clicklook": "右键点击地图进行查看",
    "cmdassist": "方向和其他命令出错时给出提示",
    "color": "给屏幕上的东西上色",
    "confirm": "攻击驯服或和平的怪物前先询问",
    "dark_room": "看不见的地面用另一种颜色",
    "dropped_nopick": "自动捡起时排除刚丢掉的东西",
    "eight_bit_tty": "把 8 位字符直接送给终端",
    "extmenu": "tty 和 curses 用菜单选择扩展命令",
    "female": "已废弃。请用 gender:female",
    "fixinv": "尽量让同一件物品保持同一个字母",
    "force_invmenu": "选择背包物品时显示菜单",
    "goldX": "按祝福状态筛选时，把金币算作未知",
    "help": "使用 / 时打印能找到的全部说明",
    "herecmd_menu": "点自己或身边一格时，列出一些可用命令",
    "hilite_pet": "高亮显示宠物",
    "hilite_pile": "高亮显示叠在一起的物品",
    "ignintr": "忽略中断信号",
    "implicit_uncursed": "能省略时，背包里不写“未诅咒”",
    "legacy": "开局打印介绍",
    "lit_corridor": "看得见的暗走廊显示成亮的",
    "lootabc": "搜刮时用 a/b/c，而不用 o/i/b",
    "mail": "启用邮件",
    "mention_decor": "走过楼梯、祭坛、喷泉等时也提示",
    "mention_walls": "撞墙时提示",
    "menu_overlay": "菜单叠在画面上并靠右",
    "menucolors": "用 MENUCOLOR 给菜单行上色",
    "nudist": "开局不穿护甲",
    "null": "允许把空字符送到终端",
    "pauper": "开局没有任何随身物品",
    "perm_invent": "用永久窗口显示背包",
    "pickup_stolen": "偷来的东西不受 pickup_types 限制",
    "pickup_thrown": "投出去的东西不受 pickup_types 限制",
    "price_quotes": "未鉴定物品显示记得的标价",
    "pushweapon": "换武器时把原来的武器放进副手",
    "rawio": "允许原始输入输出",
    "reroll": "允许重掷开局物品",
    "rest_on_space": "把空格当作休息键",
    "safe_pet": "避免明知是宠物还去攻击",
    "safe_wait": "休息或搜索前必须先按 m",
    "sanity_check": "检查内部数据是否自洽",
    "showexp": "显示累计经验",
    "showrace": "用种族符号而不是职业符号表示你",
    "showvers": "在状态栏显示版本号",
    "silent": "不让终端响铃",
    "sortpack": "背包里把同类物品排在一起",
    "sparkle": "抵抗魔法时显示闪光",
    "standout": "“--More--”用醒目模式",
    "terrainstatus": "额外显示当前地形",
    "time": "显示已经过的回合数",
    "tips": "游戏中显示一些提示",
    "tombstone": "死亡时打印墓碑",
    "toptenwin": "在窗口里而不是标准输出打印十分榜",
    "travel": "若界面支持，允许用鼠标点击赶路",
    "use_darkgray": "黑色图块用粗体黑，而不用蓝",
    "use_inverse": "高亮显示已探测到的怪物",
    "verbose": "显示更多说明",
    "weaponstatus": "额外显示当前武器",
    "whatis_menu": "选择地图位置时显示菜单",
    "checkpoint": "每次换层后保存进度，便于恢复",
    "news": "启动时打印管理员的 news",
    "showscore": "显示大约累计分数",
    "timed_delay": "Unix 和 VMS 上用计时器做延迟",
    "altmeta": "Unix 和 VMS 上把 Esc 加字符当作 Meta",
    "preload_tiles": "启动时是否把图块预载入内存",
    "vt_tiledata": "在输出里插入图块数据的转义标记",
    "vt_sounddata": "在输出里插入声音数据的转义标记",
    "ascii_map": "用地图字符。打开后关闭图块。用于 Qt、X11",
    "guicolor": "curses 是否使用界面颜色",
    "hitpointbar": "在状态栏用血条显示生命。需要状态高亮",
    "popup_dialog": "用弹出对话框。curses、Qt、Windows",
    "selectsaved": "启动时列出已有存档。tty 可选",
    "splash_screen": "显示启动画面。curses、Qt、Windows",
    "tiled_map": "用图块画地图。打开后关闭字符地图",
    "menu_tab_sep": "菜单排版。不要改",
    "travel_debug": "在地图上显示赶路算法的状态",
    "wizweight": "背包里显示物品重量",
    "autounlock": "开锁门或搜刮时，用哪一个键去开锁",
    "boulder": "巨石使用的符号",
    "crash_email": "填写崩溃报告时用的邮箱",
    "crash_name": "填写崩溃报告时用的名字",
    "crash_urlmax": "崩溃报告网址的最大长度",
    "disclose": "结束时要公开哪些信息",
    "fruit": "你爱吃的水果的名字",
    "hilite_status": "状态栏高亮规则。可以写多条",
    "language": "消息语言。en 英语，zh 简体中文。不写入存档",
    "menustyle": "多选物品的界面。Traditional、Combination、Full、Partial",
    "menu_objsyms": "菜单里是否显示物品类别符号。0 到 5",
    "msg_window": "^P 如何回看消息。tty 与 curses 的取值不同",
    "number_pad": "用字母还是数字键移动。-1 到 4",
    "packorder": "背包里各类物品的默认符号顺序",
    "paranoid_confirmation": "哪些危险动作要额外确认",
    "perminv_mode": "永久背包窗口的模式",
    "pickup_types": "自动捡起哪些符号的物品",
    "pile_limit": "走过地上物品时，多少件算作一堆",
    "runmode": "跑动时多久刷新一次地图",
    "scores": "分数榜显示哪些名次",
    "sortloot": "查看一堆物品时的排序",
    "statuslines": "状态栏用 2 行还是 3 行",
    "versinfo": "showvers 显示哪些版本信息",
    "whatis_coord": "查看时是否附带地图坐标",
    "align": "开局阵营。lawful、neutral、chaotic 或 random",
    "catname": "开局宠物是猫时的名字",
    "dogname": "开局宠物是狗时的名字",
    "gender": "开局性别。male、female 或 random",
    "horsename": "开局宠物是小马时的名字",
    "name": "角色名。多人系统上默认是用户名",
    "pettype": "偏好的宠物。cat、dog、horse、random 或 none",
    "playmode": "普通、不计分的探索，或调试",
    "race": "开局种族，例如 Human、Elf",
    "role": "开局职业，例如 Barbarian、Valkyrie",
    "quick_farsight": "远看时光标移动得更快",
    "status_updates": "是否刷新状态栏",
    "whatis_moveskip": "查看时自动跳过哪些格子",
    "monpolycontrol": "控制怪物的变形",
    "montelecontrol": "控制怪物的传送",
    "pickup_burden": "自动捡起时是否考虑负重",
    "sortdiscoveries": "已发现物品列表的排序",
    "sortvanquished": "消灭记录的排序",
    "statushilites": "状态栏高亮。也可写成 hilite_status",
    "suppress_alert": "不再显示这个版本以前的提醒",
    "whatis_filter": "查看时过滤怪物、物品或地形",
    "msghistory": "记住多少条最近的消息",
    "symset": "地图符号集的名字",
    "roguesymset": "游侠关使用的符号集",
    "windowtype": "界面。tty、curses、X11 等",
}


def write_cmdhelp() -> None:
    src = (ROOT / "dat" / "cmdhelp").read_text(encoding="utf-8", errors="replace")
    out = ["# 简体中文命令说明。键位和 & 条件与英文文件相同。", ""]
    for line in src.splitlines():
        if not line or line.startswith("&") or "\t" not in line:
            out.append(line)
            continue
        key, desc = line.split("\t", 1)
        text = wrap_note(f"{key}\t{cmd_desc(desc.strip())}")
        out.append(text)
    path = ROOT / "dat" / "locale" / "zh" / "cmdhelp"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_opthelp() -> None:
    src = (ROOT / "dat" / "opthelp").read_text(encoding="utf-8", errors="replace").splitlines()
    seen = []
    for line in src:
        m = re.match(r"^([a-z][A-Za-z0-9_]*|BIOS)(\s+)(\S.*)$", line)
        if not m:
            continue
        name, gap, rest = m.group(1), m.group(2), m.group(3)
        if len(gap) < 2 and "[" not in rest:
            continue
        if name not in seen:
            seen.append(name)
    missing = [name for name in seen if name not in OPT]
    if missing:
        raise SystemExit("missing option glosses: " + ", ".join(missing))
    lines = [
        "布尔选项和复合选项。方括号里是常见默认值。",
        "选项名必须用英文写进配置，例如 OPTIONS=language:zh 。",
        "游戏里按 O 可以查看这一份构建实际有哪些选项。",
        "只在开局前生效的项，进游戏后不能在菜单里改。",
        "语言可以在游戏里改，而且不写入存档。",
        "",
        "布尔选项：",
    ]
    bool_names = {
        "acoustics", "armorstatus", "autodescribe", "autodig", "autoopen",
        "autopickup", "autoquiver", "BIOS", "blind", "bones", "clicklook",
        "cmdassist", "color", "confirm", "dark_room", "dropped_nopick",
        "eight_bit_tty", "extmenu", "female", "fixinv", "force_invmenu",
        "goldX", "help", "herecmd_menu", "hilite_pet", "hilite_pile",
        "ignintr", "implicit_uncursed", "legacy", "lit_corridor", "lootabc",
        "mail", "mention_decor", "mention_walls", "menu_overlay", "menucolors",
        "nudist", "null", "pauper", "perm_invent", "pickup_stolen",
        "pickup_thrown", "price_quotes", "pushweapon", "rawio", "reroll",
        "rest_on_space", "safe_pet", "safe_wait", "sanity_check", "showexp",
        "showrace", "showvers", "silent", "sortpack", "sparkle", "standout",
        "terrainstatus", "time", "tips", "tombstone", "toptenwin", "travel",
        "use_darkgray", "use_inverse", "verbose", "weaponstatus", "whatis_menu",
        "checkpoint", "news", "showscore", "timed_delay",
    }
    for name in seen:
        gloss = OPT[name]
        if name in bool_names:
            line = f"{name:<18}{gloss}"
        else:
            line = f"{name:<18}{gloss}"
        lines.append(wrap_note(line))
    # Names documented above but not present in this tree's opthelp.
    for name in ("language", "symset", "roguesymset", "windowtype"):
        if name not in seen:
            lines.append(wrap_note(f"{name:<18}{OPT[name]}"))
    path = ROOT / "dat" / "locale" / "zh" / "opthelp"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"opthelp options {len(seen)}")


if __name__ == "__main__":
    write_cmdhelp()
    write_opthelp()
    print("wrote cmdhelp and opthelp")
