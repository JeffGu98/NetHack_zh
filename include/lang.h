/* NetHack 5.0	lang.h	$NHDT-Date: 1760920000 2026/10/20 00:00:00 $  $NHDT-Branch: lang-zh $:$NHDT-Revision: 1.0 $ */
/* NetHack may be freely redistributed.  See license for details. */

#ifndef LANG_H
#define LANG_H

#define LANG_EN 0
#define LANG_ZH 1

#ifdef NH_LANG_STANDALONE
typedef int boolean;
#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif
#endif

/* Current language id: LANG_EN or LANG_ZH. */
extern int nh_lang_id(void);
extern boolean nh_lang_is_zh(void);

/* Accept en, en_US, english, zh, zh_CN, chinese, and 中文.
   Unknown names return FALSE and leave the current language unchanged. */
extern boolean nh_lang_set(const char *name);
extern const char *nh_lang_name(void);

/* Replace the in-memory catalog with the file at path.
   English mode does not consult the table, but loading is still allowed. */
extern boolean nh_lang_load(const char *path);

/* Same as nh_lang_load, from a whole UTF-8 buffer. The buffer is not kept. */
extern boolean nh_lang_load_mem(const char *text);

/* Reload locale/zh.txt for the current language. Implemented in files.c
   because it uses the game's data-file lookup. A no-op in English mode
   other than releasing a previously loaded table. */
extern void nh_lang_reload(void);

/* While held, nh_tr and nh_lang_is_zh behave as English. Nestable.
   Used so encyclopedia keys and other logic stay on English names. */
extern void nh_lang_hold(boolean hold);

/* Exact lookup. A non-NULL msgid always yields a non-NULL result.
   English mode, a missing entry, or an empty msgstr returns msgid. */
extern const char *nh_tr(const char *msgid);

/* Like nh_tr, but a msgstr whose printf conversions differ from msgid
   is ignored and msgid is returned. */
extern const char *nh_trf(const char *fmt);

/* Display columns of a UTF-8 string. ASCII is 1, CJK and fullwidth are 2.
   A NULL or empty string is 0. An invalid byte counts as 1. */
extern int nh_mbswidth(const char *s);

extern void nh_lang_free(void);

#endif /* LANG_H */
