"""Builds data.js from the speaker notes of the Module 2 deck. Run: python3 build_data.py"""
import json, os, re
from pptx import Presentation
import content as C

DECK = os.path.expanduser("~/Desktop/AU/MAI 630/Modulo 2/Slides/MAI630_Module2_Class_en.pptx")
HERE = os.path.dirname(os.path.abspath(__file__))
NUM_WORDS = set("""zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen
twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million point by percent quarter third eighth ninth""".split())

def slide_title(s, i):
    if i in C.TITLES: return C.TITLES[i]
    best = ("", 0)
    for sh in s.shapes:
        if not sh.has_text_frame: continue
        for para in sh.text_frame.paragraphs:
            t = "".join(r.text for r in para.runs).strip()
            sz = max([r.font.size.pt for r in para.runs if r.font.size] or [0])
            if t and sz > best[1]: best = (t, sz)
    return best[0]

def clean(note):
    """Paragraphs to practise: without the reminders for the presenter (▶ ON THE PC, (When you come back.))."""
    out = []
    for p in note.split("\n"):
        p = p.strip()
        if not p or p.startswith("▶"): continue
        out.append(re.sub(r"^\(When you come back\.\)\s*", "", p))
    return out

def numbers(paras):
    """Number pairs of a slide in order of appearance: what is said + its figures."""
    seen, out = set(), []
    for p in paras:
        for m in re.finditer(r"\(([^()]*\d[^()]*)\)", p):
            fig = m.group(1)
            before = p[:m.start()].rstrip().split()
            if fig in C.NAMED and C.NAMED[fig]:
                said = C.NAMED[fig]
            else:
                words = []
                for w in reversed(before):
                    if words and w[-1] in ",.?!:": break  # "the pink one, six (6)": the number starts after the comma
                    parts = w.strip(",.?!:").lower().split("-")
                    if all(x in NUM_WORDS for x in parts): words.insert(0, w.strip(",.?!:"))
                    elif w.lower() == "november": words.insert(0, w)
                    else: break
                while words and words[0].lower() == "by": words.pop(0)  # "divided by two (2)"
                said = " ".join(words)
            if not said: print("NO WORDS", fig, "|", p[max(0, m.start() - 50):m.end()]); continue
            said = said[0].lower() + said[1:] if not said.startswith(("ResNet", "YOLO", "November", "CC")) else said
            key = (said, fig)
            if key not in seen: seen.add(key); out.append({"en": f"{said} ({fig})", "d": fig, "w": said})
    return out

SEP = {"/": " slash ", "_": " underscore ", ".": " dot ", "-": " dash "}
PIECE = {"src": "source", "py": "pie", "md": "M D", "cnn": "C N N", "ipynb": "I P Y N B", "claude": "Claude", "CLAUDE": "Claude", "LOG": "log", "SKILL": "skill", "<name>": "name", "module2": "module two"}
def spoken_name(tok):
    out = ""
    for part in re.split(r"([/_.\-])", tok):
        if part in SEP: out += SEP[part]
        elif part: out += PIECE.get(part, part)
    return re.sub(r"\s+", " ", out).strip()

prs = Presentation(DECK)
slides = []
all_notes, names = "", set()
for i, s in enumerate(prs.slides, 1):
    paras = clean(s.notes_slide.notes_text_frame.text)
    slides.append({"n": i, "title": slide_title(s, i), "paras": paras})
    all_notes += "\n".join(paras) + "\n"
    for p in paras:
        for tok in re.findall(r"[\w.<>/\-]*[\w>](?:[/_.][\w.<>/\-]*[\w>])+|\.[a-z]+/[a-z]+|\.gitignore", re.sub(r"\([^()]*\d[^()]*\)|^\d+\.\s", "", p)):
            if not re.fullmatch(r"[\d./,]+", tok): names.add(tok)

spoken = {t: spoken_name(t) for t in names}
for t in C.TERMS:
    if re.search(r"[/_.]", t): spoken[t] = spoken_name(t)
spoken.update(C.EXTRA_SPOKEN)

words = lambda s: len(re.sub(r"\([^()]*\d[^()]*\)|^\d+\.\s", "", s).split())
sections = []
for pid, title, a, b, cl in C.PARTS:
    tops = []
    for sl in slides[a - 1:b]:
        tops.append({"id": f"s{sl['n']}", "n": sl["n"], "title": f"Slide {sl['n']} · {sl['title']}", "w": sum(words(p) for p in sl["paras"]),
                     "items": [{"en": p} for p in sl["paras"]]})
    sections.append({"id": pid, "group": "slides", "cl": cl, "title": title, "sub": f"Class {cl} · slides {a} to {b}", "tag": f"Class {cl}", "unit": "párrafos", "topics": tops})

num_topics = []
for sl in slides:
    pairs = numbers(sl["paras"])
    if pairs: num_topics.append({"id": f"n{sl['n']}", "n": sl["n"], "kind": "numbers", "title": f"Slide {sl['n']} numbers", "items": pairs})
sections.append({"id": "numbers", "group": "numbers", "title": "Numbers", "sub": "Los números de cada slide: escúchalos o ponte a prueba", "tag": "Training", "unit": "números", "topics": num_topics})

def where(sentence):
    assert sentence in all_notes, "not in the notes: " + sentence
    return next(sl["n"] for sl in slides if any(sentence in p for p in sl["paras"]))
hard = [{"id": "terms", "kind": "hard", "title": "Technical words", "items": [{"en": t} for t in C.TERMS]}]
for tid, title, lst in (("hard21", "Hard sentences · Class 2.1", C.HARD_21), ("hard22", "Hard sentences · Class 2.2", C.HARD_22)):
    hard.append({"id": tid, "kind": "hard", "title": title, "items": [{"en": x, "src": f"Slide {where(x)}"} for x in lst]})
sections.append({"id": "hard", "group": "hard", "title": "Hard parts", "sub": "Lo más difícil de leer, cada vez más rápido y contra el reloj", "tag": "Training", "unit": "frases", "topics": hard})

phr = [{"id": f"ph{k}", "title": t, "items": [{"en": e, "src": "From your class" if w == "yours" else "Common phrase"} for w, e in lst]} for k, (t, lst) in enumerate(C.PHRASES)]
sections.append({"id": "phrases", "group": "phrases", "title": "Typical phrases", "sub": "Lo que dice un presentador: las tuyas y otras muy comunes", "tag": "Training", "unit": "frases", "topics": phr})

from contractions import contract
for sec in sections:
    for t in sec["topics"]:
        for it in t["items"]:
            it["en"] = contract(it["en"])
open(os.path.join(HERE, "data.js"), "w").write("/* Generated by build_data.py — edit content.py or the deck, not this file. */\nwindow.SECTIONS = "
    + json.dumps(sections, ensure_ascii=False) + ";\nwindow.SPOKEN = " + json.dumps(spoken, ensure_ascii=False, indent=0) + ";\n")
n = sum(len(t["items"]) for s in sections if s["group"] == "slides" for t in s["topics"])
print("slides", len(slides), "paragraphs", n, "number topics", len(num_topics), "number pairs", sum(len(t["items"]) for t in num_topics))
print("cue left:", [p[:40] for sl in slides for p in sl["paras"] if "ON THE PC" in p or "When you come back" in p])
