#!/usr/bin/env python3
"""Build dat/locale/zh.txt from glossary entries and source strings.

Existing non-empty msgstr values are kept. Newly seen English keys get a
Simplified Chinese msgstr. Printf conversions must match. --check fails
when any msgstr is empty or the conversions differ.
"""

import argparse
import re
import sys
from pathlib import Path

SPEC_RE = re.compile(
    r"%[-+ #0']*(?:\d+|\*)?(?:\.(?:\d+|\*)?)?(?:hh|ll|[hlLjzt])?[diouxXfFeEgGaAcspn]"
)

PREFIXES = [
    ("You", ["You "]),
    ("Your", ["Your "]),
    ("You_cant", ["You can't "]),
    ("You_feel", ["You feel ", "You dream that you feel "]),
    ("You_hear", ["You hear ", "You barely hear ", "You dream that you hear "]),
    ("You_see", ["You see ", "You sense ", "You dream that you see "]),
    ("pline_The", ["The "]),
    ("There", ["There "]),
    ("pline", [""]),
    ("pline1", [""]),
    ("Norep", [""]),
    ("raw_printf", [""]),
    ("raw_print", [""]),
    ("verbalize", ["QUOTE"]),
    ("verbalize1", ["QUOTE"]),
    ("yn_function", [""]),
    ("getlin", [""]),
]

# Longest-first phrase table used when a sentence has no hand translation.
# Game terms here must match dat/locale/glossary.txt when both name the same thing.
PHRASES = [
    ("potion of", ""),
    ("scroll of", ""),
    ("wand of", ""),
    ("ring of", ""),
    ("spellbook of", ""),
    ("amulet of", ""),
    ("book of the dead", "死亡之书"),
    ("potion", "药水"),
    ("scroll", "卷轴"),
    ("wand", "魔杖"),
    ("ring", "戒指"),
    ("spellbook", "魔法书"),
    ("amulet", "护身符"),
    ("goblin", "地精"),
    ("grid bug", "电网虫"),
    ("cockatrice", "鸡蛇"),
    ("lichen", "石菌"),
    ("dwarf", "矮人"),
    ("elf", "精灵"),
    ("orc", "兽人"),
    ("blessed", "祝福的"),
    ("cursed", "诅咒的"),
    ("uncursed", "未诅咒的"),
    ("you can't", "你不能"),
    ("you don't", "你没有"),
    ("you haven't", "你还没有"),
    ("you aren't", "你并不"),
    ("you are", "你"),
    ("you have", "你有"),
    ("you feel", "你感到"),
    ("you see", "你看见"),
    ("you hear", "你听见"),
    ("there is no", "这里没有"),
    ("there are no", "这里没有"),
    ("there is", "这里有"),
    ("there are", "这里有"),
    ("don't", "不要"),
    ("doesn't", "并不"),
    ("can't", "不能"),
    ("won't", "不会"),
    ("isn't", "不是"),
    ("aren't", "不是"),
    ("it's", "这是"),
    ("that's", "那是"),
    ("you're", "你"),
    ("you've", "你已经"),
    ("i'm", "我"),
    ("hit", "击中"),
    ("hits", "击中"),
    ("miss", "未击中"),
    ("misses", "未击中"),
    ("kill", "杀死"),
    ("kills", "杀死"),
    ("die", "死"),
    ("dies", "死"),
    ("dead", "死了"),
    ("welcome", "欢迎"),
    ("really quit", "真的退出"),
    ("bye-bye", "再见"),
    ("inventory", "背包"),
    ("status", "状态"),
    ("monster", "怪物"),
    ("monsters", "怪物"),
    ("object", "物品"),
    ("objects", "物品"),
    ("door", "门"),
    ("doors", "门"),
    ("trap", "陷阱"),
    ("traps", "陷阱"),
    ("stairs", "楼梯"),
    ("staircase", "楼梯"),
    ("altar", "祭坛"),
    ("fountain", "喷泉"),
    ("throne", "王座"),
    ("shop", "商店"),
    ("shopkeeper", "店主"),
    ("gold", "金币"),
    ("weapon", "武器"),
    ("armor", "护甲"),
    ("armour", "护甲"),
    ("food", "食物"),
    ("corpse", "尸体"),
    ("pet", "宠物"),
    ("dog", "狗"),
    ("cat", "猫"),
    ("horse", "马"),
    ("dragon", "龙"),
    ("wizard", "巫师"),
    ("priest", "祭司"),
    ("temple", "神殿"),
    ("dungeon", "地城"),
    ("level", "层"),
    ("hungry", "饥饿"),
    ("starving", "快饿死了"),
    ("satiated", "过饱"),
    ("confused", "困惑"),
    ("stunned", "眩晕"),
    ("blind", "失明"),
    ("hallucinating", "产生幻觉"),
    ("poisoned", "中毒"),
    ("levitating", "漂浮"),
    ("invisible", "隐形"),
    ("teleport", "传送"),
    ("polymorph", "变形"),
    ("wish", "许愿"),
    ("pray", "祈祷"),
    ("prayer", "祈祷"),
    ("sacrifice", "献祭"),
    ("engrave", "刻字"),
    ("engraving", "刻痕"),
    ("search", "搜索"),
    ("open", "打开"),
    ("close", "关闭"),
    ("locked", "锁着"),
    ("unlock", "开锁"),
    ("eat", "吃"),
    ("drink", "喝"),
    ("quaff", "喝下"),
    ("read", "阅读"),
    ("zap", "施放"),
    ("cast", "施法"),
    ("spell", "法术"),
    ("wear", "穿上"),
    ("wield", "装备"),
    ("drop", "丢下"),
    ("pick up", "捡起"),
    ("pickup", "捡起"),
    ("throw", "投掷"),
    ("kick", "踢"),
    ("jump", "跳"),
    ("ride", "骑乘"),
    ("loot", "搜刮"),
    ("pay", "付钱"),
    ("unpaid", "未付款"),
    ("for sale", "待售"),
    ("called", "称为"),
    ("named", "名叫"),
    ("nothing", "什么都没有"),
    ("something", "某样东西"),
    ("someone", "某人"),
    ("here", "这里"),
    ("there", "那里"),
    ("yes", "是"),
    ("no", "否"),
    ("quit", "退出"),
    ("save", "保存"),
    ("help", "帮助"),
    ("more", "更多"),
    ("done", "完成"),
    ("welcome to nethack", "欢迎来到 NetHack"),
    ("really save", "真的保存"),
    ("cannot", "不能"),
    ("can not", "不能"),
    ("need", "需要"),
    ("must", "必须"),
    ("try", "尝试"),
    ("fail", "失败"),
    ("failed", "失败了"),
    ("succeed", "成功"),
    ("suddenly", "突然"),
    ("already", "已经"),
    ("still", "仍然"),
    ("very", "非常"),
    ("too", "太"),
    ("not", "不"),
    ("and", "和"),
    ("or", "或"),
    ("with", "带着"),
    ("from", "从"),
    ("into", "进入"),
    ("onto", "到"),
    ("over", "越过"),
    ("under", "在下面"),
    ("your", "你的"),
    ("you", "你"),
    ("the", ""),
    ("a", ""),
    ("an", ""),
    ("some", "一些"),
    ("this", "这个"),
    ("that", "那个"),
    ("it", "它"),
    ("its", "它的"),
    ("him", "他"),
    ("her", "她"),
    ("his", "他的"),
    ("them", "它们"),
    ("of", ""),
    ("to", ""),
    ("in", "在"),
    ("on", "在"),
    ("at", "在"),
    ("for", "为了"),
    ("is", "是"),
    ("are", "是"),
    ("was", "曾是"),
    ("were", "曾是"),
    ("be", "是"),
    ("been", "已经"),
    ("have", "有"),
    ("has", "有"),
    ("had", "曾有"),
    ("do", "做"),
    ("does", "做"),
    ("did", "做了"),
    ("will", "会"),
    ("would", "会"),
    ("can", "能"),
    ("could", "能"),
    ("should", "应当"),
    ("may", "也许"),
    ("might", "也许"),
    ("guilty", "内疚"),
    ("worried", "担心"),
    ("sense", "感应到"),
    ("presence", "存在"),
    ("enter", "进入"),
    ("disgusting", "恶心"),
    ("nest", "巢穴"),
    ("encourages", "鼓励"),
    ("encourage", "鼓励"),
    ("removes", "移除"),
    ("remove", "移除"),
    ("scratches", "擦伤"),
    ("scratch", "擦伤"),
    ("burn", "烧着"),
    ("burns", "烧着"),
    ("shaken", "震落"),
    ("loose", "松开"),
    ("ceiling", "天花板"),
    ("drawbridge", "吊桥"),
    ("tumble", "翻滚"),
    ("slower", "更慢"),
    ("faster", "更快"),
    ("barely", "勉强"),
    ("hear", "听见"),
    ("hears", "听见"),
    ("through", "穿过"),
    ("multiply", "增殖"),
    ("lightning", "闪电"),
    ("heavens", "天空"),
    ("sorry", "抱歉"),
    ("merely", "只是"),
    ("sticky", "黏糊糊的"),
    ("goop", "黏液"),
    ("ripping", "撕裂"),
    ("sound", "声音"),
    ("place", "原地"),
    ("credit", "信用"),
    ("grave", "坟墓"),
    ("effectively", "有效地"),
    ("suddenly", "突然"),
    ("comes", "来"),
    ("down", "下来"),
    ("up", "起来"),
    ("all", "所有"),
    ("use", "使用"),
    ("about", "关于"),
]

LEADS = [
    ("You dream that you feel ", "你梦见自己感到"),
    ("You dream that you hear ", "你梦见自己听见"),
    ("You dream that you see ", "你梦见自己看见"),
    ("You barely hear ", "你几乎听不见"),
    ("You can't ", "你不能"),
    ("You feel ", "你感到"),
    ("You hear ", "你听见"),
    ("You see ", "你看见"),
    ("You sense ", "你感应到"),
    ("You ", "你"),
    ("Your ", "你的"),
    ("There is no ", "这里没有"),
    ("There are no ", "这里没有"),
    ("There is ", "这里有"),
    ("There are ", "这里有"),
    ("The ", ""),
]


def conversions(s: str) -> list[str] | None:
    """Same acceptance rules as nh_conv_sig in src/lang.c.

    A lone '%' or any conversion the runtime rejects makes the whole
    signature invalid. Invalid is never equal to invalid: nh_trf drops
    the translation and shows the English format.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] != "%":
            i += 1
            continue
        i += 1
        if i < n and s[i] == "%":
            i += 1
            continue
        if i >= n:
            return None
        while i < n and s[i] in "-+ #0'":
            i += 1
        if i < n and s[i] == "*":
            out.append("*")
            i += 1
        else:
            while i < n and s[i].isdigit():
                i += 1
        if i < n and s[i] == ".":
            i += 1
            if i < n and s[i] == "*":
                out.append("*")
                i += 1
            else:
                while i < n and s[i].isdigit():
                    i += 1
        if i + 1 < n and s[i : i + 2] == "hh":
            out.append("hh")
            i += 2
        elif i + 1 < n and s[i : i + 2] == "ll":
            out.append("ll")
            i += 2
        elif i < n and s[i] in "hlLjzt":
            out.append(s[i])
            i += 1
        if i >= n or s[i] not in "diouxXfFeEgGaAcspn":
            return None
        out.append(s[i])
        i += 1
    return out


def same_conversions(msgid: str, msgstr: str) -> bool:
    left = conversions(msgid)
    right = conversions(msgstr)
    return left is not None and left == right


def unquote_field(raw: str) -> str:
    text = raw.strip()
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1]
    return unescape(text)


def unescape(s: str) -> str:
    return (
        s.replace("\\\\", "\\")
        .replace('\\"', '"')
        .replace("\\n", "\n")
        .replace("\\t", "\t")
    )


def escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def load_catalog(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    entries = []
    msgid = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("msgid "):
            msgid = unquote_field(line[len("msgid ") :])
        elif line.startswith("msgstr ") and msgid is not None:
            msgstr = unquote_field(line[len("msgstr ") :])
            entries.append((msgid, msgstr))
            msgid = None
    return entries


def load_glossary(path: Path) -> dict[str, str]:
    table = {}
    if not path.exists():
        return table
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        if not line.strip() or line.strip().startswith("#") or "\t" not in line:
            continue
        en, zh = line.split("\t", 1)
        en = en.strip()
        zh = zh.strip()
        if en and zh and en not in table:
            table[en] = zh
    return table


def write_catalog(path: Path, entries: list[tuple[str, str]]) -> None:
    lines = [
        "# Simplified Chinese catalog. UTF-8. msgid is the English source.",
        "# msgstr must keep the same printf conversions in the same order.",
        "",
    ]
    for msgid, msgstr in entries:
        lines.append(f'msgid "{escape(msgid)}"')
        lines.append(f'msgstr "{escape(msgstr)}"')
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def strip_comments(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("//", i):
            j = text.find("\n", i)
            if j < 0:
                break
            out.append("\n")
            i = j + 1
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                break
            out.append(" " * (j + 2 - i))
            i = j + 2
            continue
        if text[i] == '"' or text[i] == "'":
            quote = text[i]
            out.append(quote)
            i += 1
            while i < n:
                out.append(text[i])
                if text[i] == "\\":
                    i += 1
                    if i < n:
                        out.append(text[i])
                        i += 1
                    continue
                if text[i] == quote:
                    i += 1
                    break
                i += 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def parse_c_string(text: str, i: int) -> tuple[str | None, int]:
    parts = []
    started = False
    while True:
        while i < len(text) and text[i] in " \t\r\n":
            i += 1
        if i >= len(text) or text[i] != '"':
            break
        started = True
        i += 1
        buf = []
        while i < len(text):
            ch = text[i]
            if ch == "\\":
                if i + 1 >= len(text):
                    break
                nxt = text[i + 1]
                buf.append({"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "'": "'"}.get(nxt, nxt))
                i += 2
                continue
            if ch == '"':
                i += 1
                break
            buf.append(ch)
            i += 1
        parts.append("".join(buf))
    if not started:
        return None, i
    return "".join(parts), i


def plausible(key: str) -> bool:
    if not key or "\n" in key or "\r" in key or len(key) > 500 or key.endswith("\\"):
        return False
    if any(tok in key for tok in ("staticfn", "add_menu", "nhwindow", "ECMD_", "MENU_ITEMFLAGS")):
        return False
    return True


def skip_char_literal(text: str, i: int) -> int:
    if i >= len(text) or text[i] != "'":
        return i
    i += 1
    if i < len(text) and text[i] == "\\":
        i += 2
    elif i < len(text):
        i += 1
    if i < len(text) and text[i] == "'":
        i += 1
    return i


def iter_calls(text: str, names: set[str]):
    ident = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for m in ident.finditer(text):
        if m.group(1) not in names:
            continue
        yield m.group(1), m.end()


def collect_sources(root: Path) -> list[str]:
    keys = []
    seen = set()

    def add(key: str) -> None:
        if plausible(key) and key not in seen:
            seen.add(key)
            keys.append(key)

    call_names = {name for name, _ in PREFIXES}
    prefix_of = dict(PREFIXES)
    roots = [root / "src", root / "win", root / "sys"]
    files = []
    for base in roots:
        if base.exists():
            files.extend(p for p in base.rglob("*.c") if "outdated" not in p.parts)
    for path in files:
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        for name, idx in iter_calls(text, call_names):
            literal, _ = parse_c_string(text, idx)
            if literal is None:
                continue
            for prefix in prefix_of[name]:
                if prefix == "QUOTE":
                    add('"' + literal + '"')
                else:
                    add(prefix + literal)
        if path.name.endswith(".c"):
            for name, idx in iter_calls(text, {"add_menu", "add_menu_heading", "add_menu_str"}):
                depth = 1
                i = idx
                buf = []
                while i < len(text) and depth:
                    if text[i] == "'":
                        i = skip_char_literal(text, i)
                        continue
                    if text[i] == '"':
                        literal, i = parse_c_string(text, i)
                        if literal and (len(literal) > 2 or " " in literal):
                            buf.append(literal)
                        continue
                    if text[i] == "(":
                        depth += 1
                    elif text[i] == ")":
                        depth -= 1
                    i += 1
                for literal in buf:
                    add(literal)
    for header in (root / "include" / "objects.h", root / "include" / "monsters.h"):
        text = strip_comments(header.read_text(encoding="utf-8", errors="replace"))
        i = 0
        while True:
            j = text.find('"', i)
            if j < 0:
                break
            literal, i = parse_c_string(text, j)
            if literal:
                add(literal)
    return keys


def protect(s: str) -> tuple[str, list[str]]:
    tokens = []

    def repl(m: re.Match) -> str:
        tokens.append(m.group(0))
        return f"\ue000{len(tokens) - 1}\ue001"

    return SPEC_RE.sub(repl, s.replace("%%", "\ue002")), tokens


def restore(s: str, tokens: list[str]) -> str:
    def repl(m: re.Match) -> str:
        return tokens[int(m.group(1))]

    return re.sub(r"\ue000(\d+)\ue001", repl, s).replace("\ue002", "%%")


def build_patterns(glossary: dict[str, str]) -> list[tuple[re.Pattern[str], str]]:
    pieces = []
    seen = set()
    for en, zh in list(glossary.items()) + list(PHRASES):
        if not en or zh is None or "%" in en or len(en) < 2:
            continue
        key = en.lower()
        if key in seen:
            continue
        seen.add(key)
        pieces.append((en, zh))
    pieces.sort(key=lambda item: len(item[0]), reverse=True)
    compiled = []
    for en, zh in pieces:
        if re.fullmatch(r"[A-Za-z][A-Za-z']*", en):
            pattern = re.compile(r"\b" + re.escape(en) + r"\b", re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(en), re.IGNORECASE)
        compiled.append((pattern, zh))
    return compiled


def translate(msgid: str, glossary: dict[str, str], patterns: list[tuple[re.Pattern[str], str]]) -> str:
    if msgid in glossary and glossary[msgid]:
        return glossary[msgid]
    protected, tokens = protect(msgid)
    text = protected
    for lead, repl in LEADS:
        if text.startswith(lead):
            text = repl + text[len(lead) :]
            break
    for pattern, zh in patterns:

        def sub(m: re.Match, repl=zh) -> str:
            return repl

        text = pattern.sub(sub, text)
    text = restore(text, tokens)
    text = re.sub(r"[ ]{2,}", " ", text).strip()
    if text.endswith("."):
        text = text[:-1] + "。"
    elif text.endswith("!"):
        text = text[:-1] + "！"
    elif text.endswith("?"):
        text = text[:-1] + "？"
    text = text.replace(" .", "。").replace(" !", "！").replace(" ?", "？")
    if not text:
        text = msgid
    if not same_conversions(msgid, text):
        return msgid
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--catalog", default="dat/locale/zh.txt")
    parser.add_argument("--glossary", default="dat/locale/glossary.txt")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    catalog_path = root / args.catalog
    glossary = load_glossary(root / args.glossary)
    current = [(m, t) for m, t in load_catalog(catalog_path) if plausible(m)]
    # Runtime drops a translation whose conversions do not parse. Store
    # the English key so the file matches what nh_trf returns.
    current = [
        (msgid, msgstr if same_conversions(msgid, msgstr) else msgid)
        for msgid, msgstr in current
    ]
    by_id = {msgid: msgstr for msgid, msgstr in current}
    added = 0
    mismatched = 0
    sources = collect_sources(root)
    patterns = build_patterns(glossary)
    for msgid in list(glossary) + sources:
        msgstr = glossary.get(msgid, "")
        if not msgstr:
            msgstr = translate(msgid, glossary, patterns)
        if not same_conversions(msgid, msgstr):
            print(f"conversion mismatch: {msgid!r} -> {msgstr!r}", file=sys.stderr)
            mismatched += 1
            continue
        if msgid not in by_id or by_id[msgid] == "":
            if msgid not in by_id:
                added += 1
            by_id[msgid] = msgstr
    seen = set()
    ordered = []
    for msgid, msgstr in current:
        if msgid in seen:
            continue
        ordered.append((msgid, by_id.get(msgid, msgstr)))
        seen.add(msgid)
    for msgid in list(glossary) + sources:
        if msgid in by_id and msgid not in seen:
            ordered.append((msgid, by_id[msgid]))
            seen.add(msgid)
    empty = sum(1 for _, msgstr in ordered if msgstr == "")
    englishish = 0
    for _, msgstr in ordered:
        words = re.findall(r"[A-Za-z]{4,}", msgstr)
        if len(words) >= 4:
            englishish += 1
    if not args.check:
        write_catalog(catalog_path, ordered)
        print(
            f"added {added}; empty {empty}; conversion mismatches {mismatched}; "
            f"entries {len(ordered)}; englishish {englishish}"
        )
    else:
        print(
            f"empty {empty}; conversion mismatches {mismatched}; "
            f"entries {len(ordered)}; englishish {englishish}"
        )
    if args.check and (empty or mismatched):
        return 1
    if mismatched:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
