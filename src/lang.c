/* NetHack 5.0	lang.c	$NHDT-Date: 1760920000 2026/10/20 00:00:00 $  $NHDT-Branch: lang-zh $:$NHDT-Revision: 1.0 $ */
/* NetHack may be freely redistributed.  See license for details. */

#ifdef NH_LANG_STANDALONE
#include "lang.h"
#else
#include "hack.h"
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

struct nh_lang_slot {
    char *key;
    char *val; /* NULL when msgstr is empty */
};

static int current_lang = LANG_EN;
static int tr_hold = 0;
static struct nh_lang_slot *slots = NULL;
static size_t slot_cap = 0;
static size_t slot_used = 0;

int
nh_lang_id(void)
{
    return current_lang;
}

boolean
nh_lang_is_zh(void)
{
    return current_lang == LANG_ZH && tr_hold == 0;
}

void
nh_lang_hold(boolean hold)
{
    if (hold)
        tr_hold++;
    else if (tr_hold > 0)
        tr_hold--;
}

const char *
nh_lang_name(void)
{
    return current_lang == LANG_ZH ? "zh" : "en";
}

boolean
nh_lang_set(const char *name)
{
    int id;

    if (!name)
        return FALSE;
    if (!strcmp(name, "en") || !strcmp(name, "en_US") || !strcmp(name, "english"))
        id = LANG_EN;
    else if (!strcmp(name, "zh") || !strcmp(name, "zh_CN")
             || !strcmp(name, "chinese") || !strcmp(name, "中文"))
        id = LANG_ZH;
    else
        return FALSE;
    current_lang = id;
    return TRUE;
}

void
nh_lang_free(void)
{
    size_t i;

    if (!slots)
        return;
    for (i = 0; i < slot_cap; i++) {
        free(slots[i].key);
        free(slots[i].val);
    }
    free(slots);
    slots = NULL;
    slot_cap = 0;
    slot_used = 0;
}

static unsigned
nh_hash(const char *s)
{
    unsigned h = 5381;

    while (*s)
        h = ((h << 5) + h) + (unsigned char) *s++;
    return h;
}

static int
nh_grow(size_t need)
{
    struct nh_lang_slot *fresh;
    size_t ncap, i;

    if (slot_cap > 0 && slot_used * 10 < slot_cap * 7 && slot_used + need <= slot_cap)
        return 1;
    ncap = slot_cap ? slot_cap * 2 : 1024;
    while (ncap < (slot_used + need) * 2)
        ncap *= 2;
    fresh = (struct nh_lang_slot *) calloc(ncap, sizeof *fresh);
    if (!fresh)
        return 0;
    for (i = 0; i < slot_cap; i++) {
        unsigned h;
        size_t j;

        if (!slots[i].key)
            continue;
        h = nh_hash(slots[i].key);
        j = h % ncap;
        while (fresh[j].key)
            j = (j + 1) % ncap;
        fresh[j] = slots[i];
    }
    free(slots);
    slots = fresh;
    slot_cap = ncap;
    return 1;
}

static struct nh_lang_slot *
nh_find(const char *key, int insert)
{
    unsigned h;
    size_t j, start;

    if (!key || !slot_cap)
        return NULL;
    h = nh_hash(key);
    start = j = h % slot_cap;
    do {
        if (!slots[j].key) {
            if (!insert)
                return NULL;
            if (slot_used * 10 >= slot_cap * 7) {
                if (!nh_grow(1))
                    return NULL;
                return nh_find(key, 1);
            }
            return &slots[j];
        }
        if (!strcmp(slots[j].key, key))
            return &slots[j];
        j = (j + 1) % slot_cap;
    } while (j != start);
    return NULL;
}

static void
nh_insert(const char *key, const char *val)
{
    struct nh_lang_slot *slot;
    char *kcopy, *vcopy;

    if (!slot_cap && !nh_grow(1))
        return;
    slot = nh_find(key, 1);
    if (!slot)
        return;
    if (slot->key) {
        free(slot->val);
        slot->val = NULL;
        if (val && val[0]) {
            vcopy = strdup(val);
            if (vcopy)
                slot->val = vcopy;
        }
        return;
    }
    kcopy = strdup(key);
    if (!kcopy)
        return;
    vcopy = NULL;
    if (val && val[0]) {
        vcopy = strdup(val);
        if (!vcopy) {
            free(kcopy);
            return;
        }
    }
    slot->key = kcopy;
    slot->val = vcopy;
    slot_used++;
}

const char *
nh_tr(const char *msgid)
{
    struct nh_lang_slot *slot;

    if (!msgid)
        return NULL;
    if (current_lang != LANG_ZH || tr_hold || !slot_cap)
        return msgid;
    slot = nh_find(msgid, 0);
    if (!slot || !slot->val || !slot->val[0])
        return msgid;
    return slot->val;
}

/* Build a signature of printf conversions: length modifiers, '*'
   argument consumers, and the conversion character. "%%" is skipped. */
static int
nh_conv_sig(const char *s, char *out, size_t outsz)
{
    size_t n = 0;

    if (!s)
        s = "";
    while (*s) {
        if (*s != '%') {
            s++;
            continue;
        }
        s++;
        if (*s == '%') {
            s++;
            continue;
        }
        if (*s == '\0')
            return -1;
        while (*s && strchr("-+ #0'", *s))
            s++;
        if (*s == '*') {
            if (n + 1 >= outsz)
                return -1;
            out[n++] = '*';
            s++;
        } else {
            while (*s >= '0' && *s <= '9')
                s++;
        }
        if (*s == '.') {
            s++;
            if (*s == '*') {
                if (n + 1 >= outsz)
                    return -1;
                out[n++] = '*';
                s++;
            } else {
                while (*s >= '0' && *s <= '9')
                    s++;
            }
        }
        if (s[0] == 'h' && s[1] == 'h') {
            if (n + 2 >= outsz)
                return -1;
            out[n++] = 'h';
            out[n++] = 'h';
            s += 2;
        } else if (s[0] == 'l' && s[1] == 'l') {
            if (n + 2 >= outsz)
                return -1;
            out[n++] = 'l';
            out[n++] = 'l';
            s += 2;
        } else if (*s && strchr("hlLjzt", *s)) {
            if (n + 1 >= outsz)
                return -1;
            out[n++] = *s++;
        }
        if (*s == '\0' || !strchr("diouxXfFeEgGaAcspn", *s))
            return -1;
        if (n + 2 >= outsz)
            return -1;
        out[n++] = *s++;
        out[n++] = ';';
    }
    if (n >= outsz)
        return -1;
    out[n] = '\0';
    return 0;
}

const char *
nh_trf(const char *fmt)
{
    const char *tr;
    char a[256], b[256];

    if (!fmt)
        return NULL;
    tr = nh_tr(fmt);
    if (tr == fmt)
        return fmt;
    if (nh_conv_sig(fmt, a, sizeof a) != 0 || nh_conv_sig(tr, b, sizeof b) != 0)
        return fmt;
    if (strcmp(a, b) != 0)
        return fmt;
    return tr;
}

static int
nh_utf8_decode(const char *s, uint32_t *cp, int *used)
{
    const unsigned char *u = (const unsigned char *) s;
    unsigned char c;

    if (!u || !u[0])
        return 0;
    c = u[0];
    if (c < 0x80) {
        *cp = c;
        *used = 1;
        return 1;
    }
    if ((c & 0xE0) == 0xC0 && u[1] && (u[1] & 0xC0) == 0x80) {
        *cp = ((uint32_t) (c & 0x1F) << 6) | (u[1] & 0x3F);
        *used = 2;
        if (*cp < 0x80)
            return 0;
        return 1;
    }
    if ((c & 0xF0) == 0xE0 && u[1] && u[2]
        && (u[1] & 0xC0) == 0x80 && (u[2] & 0xC0) == 0x80) {
        *cp = ((uint32_t) (c & 0x0F) << 12) | ((uint32_t) (u[1] & 0x3F) << 6)
              | (u[2] & 0x3F);
        *used = 3;
        if (*cp < 0x800)
            return 0;
        return 1;
    }
    if ((c & 0xF8) == 0xF0 && u[1] && u[2] && u[3]
        && (u[1] & 0xC0) == 0x80 && (u[2] & 0xC0) == 0x80
        && (u[3] & 0xC0) == 0x80) {
        *cp = ((uint32_t) (c & 0x07) << 18) | ((uint32_t) (u[1] & 0x3F) << 12)
              | ((uint32_t) (u[2] & 0x3F) << 6) | (u[3] & 0x3F);
        *used = 4;
        if (*cp < 0x10000 || *cp > 0x10FFFF)
            return 0;
        return 1;
    }
    return 0;
}

static int
nh_wide(uint32_t cp)
{
    if (cp >= 0x1100 && cp <= 0x115F)
        return 1;
    if (cp >= 0x2329 && cp <= 0x232A)
        return 1;
    if (cp >= 0x2E80 && cp <= 0xA4CF)
        return 1;
    if (cp >= 0xAC00 && cp <= 0xD7A3)
        return 1;
    if (cp >= 0xF900 && cp <= 0xFAFF)
        return 1;
    if (cp >= 0xFE10 && cp <= 0xFE19)
        return 1;
    if (cp >= 0xFE30 && cp <= 0xFE6F)
        return 1;
    if (cp >= 0xFF01 && cp <= 0xFF60)
        return 1;
    if (cp >= 0xFFE0 && cp <= 0xFFE6)
        return 1;
    if (cp >= 0x1F300 && cp <= 0x1F64F)
        return 1;
    if (cp >= 0x20000 && cp <= 0x3FFFD)
        return 1;
    return 0;
}

int
nh_mbswidth(const char *s)
{
    int cols = 0;

    if (!s)
        return 0;
    while (*s) {
        uint32_t cp = 0;
        int used = 1;

        if (!nh_utf8_decode(s, &cp, &used)) {
            cols += 1;
            s += 1;
            continue;
        }
        cols += nh_wide(cp) ? 2 : 1;
        s += used;
    }
    return cols;
}

static char *
nh_unquote(const char *line, const char *keyword)
{
    size_t klen = strlen(keyword);
    const char *p;
    char *out;
    size_t n = 0, cap = 64;

    while (*line == ' ' || *line == '\t')
        line++;
    if (strncmp(line, keyword, klen) != 0)
        return NULL;
    p = line + klen;
    if (*p != ' ' && *p != '\t')
        return NULL;
    while (*p == ' ' || *p == '\t')
        p++;
    if (*p != '"')
        return NULL;
    p++;
    out = (char *) malloc(cap);
    if (!out)
        return NULL;
    while (*p && *p != '"') {
        char ch = *p++;

        if (ch == '\\') {
            if (*p == '\0') {
                free(out);
                return NULL;
            }
            ch = *p++;
            if (ch == 'n')
                ch = '\n';
            else if (ch == 't')
                ch = '\t';
            else if (ch == '\\' || ch == '"')
                ;
            else {
                free(out);
                return NULL;
            }
        }
        if (n + 1 >= cap) {
            char *grown;
            cap *= 2;
            grown = (char *) realloc(out, cap);
            if (!grown) {
                free(out);
                return NULL;
            }
            out = grown;
        }
        out[n++] = ch;
    }
    if (*p != '"') {
        free(out);
        return NULL;
    }
    out[n] = '\0';
    return out;
}

boolean
nh_lang_load_mem(const char *text)
{
    char *copy, *line, *next;
    char *pending = NULL;
    int ok = TRUE;

    if (!text)
        return FALSE;
    nh_lang_free();
    if (!nh_grow(1))
        return FALSE;
    copy = strdup(text);
    if (!copy) {
        nh_lang_free();
        return FALSE;
    }
    if ((unsigned char) copy[0] == 0xEF && (unsigned char) copy[1] == 0xBB
        && (unsigned char) copy[2] == 0xBF)
        memmove(copy, copy + 3, strlen(copy + 3) + 1);

    for (line = copy; line; line = next) {
        next = strchr(line, '\n');
        if (next) {
            *next = '\0';
            next++;
        }
        if (line[0] && line[strlen(line) - 1] == '\r')
            line[strlen(line) - 1] = '\0';
        if (line[0] == '\0' || line[0] == '#')
            continue;
        if (!strncmp(line, "msgid", 5)) {
            free(pending);
            pending = nh_unquote(line, "msgid");
            if (!pending) {
                ok = FALSE;
                break;
            }
            continue;
        }
        if (!strncmp(line, "msgstr", 6)) {
            char *val = nh_unquote(line, "msgstr");

            if (!pending || !val) {
                free(val);
                ok = FALSE;
                break;
            }
            nh_insert(pending, val);
            free(pending);
            free(val);
            pending = NULL;
            continue;
        }
        ok = FALSE;
        break;
    }
    if (pending)
        ok = FALSE;
    free(pending);
    free(copy);
    if (!ok) {
        nh_lang_free();
        return FALSE;
    }
    return TRUE;
}

boolean
nh_lang_load(const char *path)
{
    FILE *fp;
    long sz;
    char *buf;
    size_t nread;
    boolean ok;

    if (!path)
        return FALSE;
    fp = fopen(path, "rb");
    if (!fp)
        return FALSE;
    if (fseek(fp, 0, SEEK_END) != 0) {
        fclose(fp);
        return FALSE;
    }
    sz = ftell(fp);
    if (sz < 0) {
        fclose(fp);
        return FALSE;
    }
    if (fseek(fp, 0, SEEK_SET) != 0) {
        fclose(fp);
        return FALSE;
    }
    buf = (char *) malloc((size_t) sz + 1);
    if (!buf) {
        fclose(fp);
        return FALSE;
    }
    nread = fread(buf, 1, (size_t) sz, fp);
    fclose(fp);
    buf[nread] = '\0';
    ok = nh_lang_load_mem(buf);
    free(buf);
    return ok;
}
