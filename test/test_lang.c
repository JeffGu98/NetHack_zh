/* Standalone checks for the language catalog. Not linked into the game. */
#ifndef NH_LANG_STANDALONE
#define NH_LANG_STANDALONE
#endif
#include "lang.h"

#include <stdio.h>
#include <string.h>

static int fails = 0;

static void
expect(int cond, const char *msg)
{
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg);
        fails++;
    }
}

static void
write_file(const char *path, const char *body)
{
    FILE *fp = fopen(path, "w");

    if (!fp) {
        perror(path);
        fails++;
        return;
    }
    fputs(body, fp);
    fclose(fp);
}

/* Match src/lang.c nh_unquote: \\ \" \n \t, one wrapping quote pair. */
static int
unescape_field(const char *in, char *out, size_t outsz)
{
    size_t n = 0;

    while (*in) {
        char ch = *in++;

        if (ch == '\\') {
            if (*in == '\0')
                return 0;
            ch = *in++;
            if (ch == 'n')
                ch = '\n';
            else if (ch == 't')
                ch = '\t';
            else if (ch != '\\' && ch != '"')
                return 0;
        }
        if (n + 1 >= outsz)
            return 0;
        out[n++] = ch;
    }
    out[n] = '\0';
    return 1;
}

static int
take_quoted(char *line, int skip, char *out, size_t outsz)
{
    char *body = line + skip;
    size_t len;

    len = strlen(body);
    if (len && body[len - 1] == '\n')
        body[--len] = '\0';
    if (len && body[len - 1] == '\r')
        body[--len] = '\0';
    if (!len || body[len - 1] != '"')
        return 0;
    body[len - 1] = '\0';
    return unescape_field(body, out, outsz);
}

static void
check_catalog(const char *path)
{
    FILE *fp = fopen(path, "r");
    char line[8192];
    char msgid[4096];
    char msgstr[4096];
    int have = 0, rows = 0, checked = 0;

    if (!fp) {
        perror(path);
        fails++;
        return;
    }
    expect(nh_lang_set("zh") == TRUE, "catalog language zh");
    expect(nh_lang_load(path) == TRUE, "load requested catalog");
    msgid[0] = '\0';
    while (fgets(line, sizeof line, fp)) {
        const char *got;

        if (!strncmp(line, "msgid \"", 7)) {
            if (!take_quoted(line, 7, msgid, sizeof msgid)) {
                fprintf(stderr, "FAIL catalog msgid parse: %s", line);
                fails++;
                break;
            }
            have = 1;
        } else if (have && !strncmp(line, "msgstr \"", 8)) {
            if (!take_quoted(line, 8, msgstr, sizeof msgstr)) {
                fprintf(stderr, "FAIL catalog msgstr parse: %s\n", msgid);
                fails++;
                break;
            }
            got = nh_trf(msgid);
            checked++;
            if (!msgstr[0] || !got || strcmp(got, msgstr) != 0) {
                fprintf(stderr, "FAIL catalog: [%s] got [%s] want [%s]\n",
                        msgid, got ? got : "(null)", msgstr);
                fails++;
                if (++rows > 20)
                    break;
            }
            have = 0;
        }
    }
    fclose(fp);
    expect(checked > 0, "catalog contained entries");
    if (!fails)
        fprintf(stderr, "catalog ok: %d entries\n", checked);
}

int
main(int argc, char **argv)
{
    const char *goblin = "goblin";
    const char *missing = "missing";
    const char *hit = "You hit %s.";
    const char *pct = "100%%";
    const char *p;

    expect(nh_lang_set("zh_CN") == TRUE, "set zh_CN");
    expect(nh_lang_name() && strcmp(nh_lang_name(), "zh") == 0, "name is zh");
    expect(nh_lang_set("nope") == FALSE, "reject nope");
    expect(strcmp(nh_lang_name(), "zh") == 0, "language unchanged after nope");

    expect(nh_lang_set("en") == TRUE, "set en");
    p = nh_tr(goblin);
    expect(p == goblin, "English lookup returns the same pointer");

    write_file("/tmp/nhlang_good.txt",
               "msgid \"goblin\"\n"
               "msgstr \"地精\"\n"
               "\n"
               "msgid \"You hit %s.\"\n"
               "msgstr \"你击中了%s。\"\n"
               "\n"
               "msgid \"100%%\"\n"
               "msgstr \"100%%\"\n");
    expect(nh_lang_set("zh") == TRUE, "set zh");
    expect(nh_lang_load("/tmp/nhlang_good.txt") == TRUE, "load good catalog");
    expect(strcmp(nh_tr("goblin"), "地精") == 0, "translate goblin");
    p = nh_tr(missing);
    expect(p == missing, "missing key returns the original pointer");
    expect(nh_tr(NULL) == NULL, "null msgid");
    expect(strcmp(nh_trf(hit), "你击中了%s。") == 0, "translate format");
    expect(nh_trf(pct) == pct || strcmp(nh_trf(pct), "100%%") == 0,
           "matching %% is accepted");
    expect(strcmp(nh_trf(pct), "100%%") == 0, "%% translation text");

    expect(nh_lang_is_zh() == TRUE, "is zh before hold");
    nh_lang_hold(TRUE);
    expect(nh_lang_is_zh() == FALSE, "held is not zh");
    p = nh_tr(goblin);
    expect(p == goblin, "held lookup returns the msgid pointer");
    nh_lang_hold(TRUE);
    nh_lang_hold(FALSE);
    expect(nh_lang_is_zh() == FALSE, "nested hold stays held");
    nh_lang_hold(FALSE);
    expect(nh_lang_is_zh() == TRUE, "hold released");
    expect(strcmp(nh_tr("goblin"), "地精") == 0, "translate after hold");

    write_file("/tmp/nhlang_esc.txt",
               "msgid \"say \\\"hi\\\"\\n\"\n"
               "msgstr \"说\\\"你好\\\"\\n\"\n");
    expect(nh_lang_load("/tmp/nhlang_esc.txt") == TRUE, "load escaped catalog");
    expect(strcmp(nh_tr("say \"hi\"\n"), "说\"你好\"\n") == 0, "unescape quotes");

    write_file("/tmp/nhlang_bad.txt",
               "msgid \"You hit %s.\"\n"
               "msgstr \"你击中了%d。\"\n");
    expect(nh_lang_load("/tmp/nhlang_bad.txt") == TRUE, "load mismatched catalog");
    p = nh_trf(hit);
    expect(p == hit, "mismatched conversion falls back to the original pointer");

    write_file("/tmp/nhlang_pct.txt",
               "msgid \"100%%\"\n"
               "msgstr \"100%\"\n");
    expect(nh_lang_load("/tmp/nhlang_pct.txt") == TRUE, "load broken percent");
    p = nh_trf(pct);
    expect(p == pct, "broken %% falls back to the original pointer");

    expect(nh_mbswidth("Ab") == 2, "ASCII width");
    expect(nh_mbswidth("地精") == 4, "CJK width");
    expect(nh_mbswidth("") == 0, "empty width");

    expect(nh_lang_set("chinese") == TRUE, "alias chinese");
    expect(nh_lang_set("中文") == TRUE, "alias 中文");
    expect(nh_lang_set("en_US") == TRUE, "alias en_US");
    expect(strcmp(nh_lang_name(), "en") == 0, "en_US names en");
    expect(nh_lang_set("english") == TRUE, "alias english");

    nh_lang_free();
    if (argc > 1)
        check_catalog(argv[1]);
    if (fails) {
        fprintf(stderr, "%d failed\n", fails);
        return 1;
    }
    return 0;
}
