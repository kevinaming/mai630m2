"""Spoken-English contractions (I will → I'll, you are → you're, do not → don't) for the phrases read aloud."""
import re

PARTICIPLE = (r"(?:been|done|seen|made|gone|taken|written|given|found|got|gotten|had|put|read|said|told|heard|known|shown|sent|built|lost|run|left|"
              r"understood|chosen|broken|forgotten|begun|\w+ed)")
# Next word required: "Yes, it is." and "where you are." keep both words.
WORD = r"(?=\s+[\w\"'(])"
NOT = [("cannot", "can't"), ("can not", "can't"), ("will not", "won't"), ("do not", "don't"), ("does not", "doesn't"), ("did not", "didn't"),
       ("should not", "shouldn't"), ("would not", "wouldn't"), ("could not", "couldn't"), ("have not", "haven't"), ("has not", "hasn't"), ("had not", "hadn't")]
SUBJECT_NOT = [("I am not", "I'm not"), ("you are not", "you're not"), ("we are not", "we're not"), ("they are not", "they're not"),
               ("he is not", "he's not"), ("she is not", "she's not"), ("it is not", "it's not"), ("that is not", "that's not"),
               ("there is not", "there isn't"), ("is not", "isn't"), ("are not", "aren't"), ("was not", "wasn't"), ("were not", "weren't")]
SUBJECT = [("I am", "I'm"), ("you are", "you're"), ("we are", "we're"), ("they are", "they're"), ("he is", "he's"), ("she is", "she's"), ("it is", "it's"),
           ("that is", "that's"), ("there is", "there's"), ("here is", "here's"), ("what is", "what's"), ("who is", "who's"), ("how is", "how's"),
           ("where is", "where's"), ("when is", "when's"), ("let us", "let's"),
           ("I will", "I'll"), ("you will", "you'll"), ("we will", "we'll"), ("they will", "they'll"), ("he will", "he'll"), ("she will", "she'll"),
           ("it will", "it'll"), ("that will", "that'll"),
           ("I would", "I'd"), ("you would", "you'd"), ("we would", "we'd"), ("they would", "they'd")]
PERFECT = [("I have", "I've"), ("you have", "you've"), ("we have", "we've"), ("they have", "they've"), ("it has", "it's"), ("should have", "should've"),
           ("could have", "could've"), ("would have", "would've")]
# Where the pair is not really subject + verb, or the short form sounds wrong, both words stay:
# "the key idea here is", "the change you made there is lost", "reading it is the most", "where we are on the page".
KEEP = re.compile(r"(?:\b(?:idea|made|put|saved|stored)\s+(?:here|there)\s+is\b|\b\w+ing\s+it\s+is\b|\bwhere\s+(?:I\s+am|you\s+are|we\s+are|they\s+are|it\s+is)\b)", re.I)
RX = [(re.compile(rf"\b{re.escape(a)}\b", re.I), b) for a, b in NOT]
RX += [(re.compile(rf"\b{re.escape(a)}\b{WORD}", re.I), b) for a, b in SUBJECT_NOT + SUBJECT]
RX += [(re.compile(rf"\b{re.escape(a)}\b(?=\s+(?:not\s+|already\s+|just\s+|never\s+|also\s+)?{PARTICIPLE}\b)", re.I), b) for a, b in PERFECT]


def _keep_case(src, rep):
    return rep[0].upper() + rep[1:] if src[0].isupper() else rep


def contract(text):
    if not text or "`" in text:
        return text
    kept = {}
    def hold(m):
        key = f"\0{len(kept)}\0"
        kept[key] = m.group(0)
        return key
    text = KEEP.sub(hold, text)
    for rx, rep in RX:
        text = rx.sub(lambda m: _keep_case(m.group(0), rep), text)
    for key, val in kept.items():
        text = text.replace(key, val)
    return text
