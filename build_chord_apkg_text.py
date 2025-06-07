# build_chord_apkg_text.py
#
# Делает .apkg без картинок, но с нотами и краткими метками ПР / ЛР.
# Строки берёт из cards.txt (пример формата см. ниже).
#
# Требования:  pip install genanki

from pathlib import Path
import re, genanki

TXT_FILE  = Path("cards.txt")          # список строк
DECK_NAME = "Инверсия (текст)"
APKG_FILE = "triads_text.apkg"

NOTE_ORDER = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
MAJOR, MINOR, DIM = [0,4,7], [0,3,7], [0,3,6]

def triad(ch):
    root = re.match(r'^([A-G][#b]?)(.*)$', ch).group(1)        # C  или  B♭
    qual = ch[len(root):]                                      # '', m, dim
    idx  = NOTE_ORDER.index(root.replace('b', '#'))
    steps = MINOR if qual=='m' else DIM if 'dim' in qual else MAJOR
    return [NOTE_ORDER[(idx+s)%12].replace('#','♯') for s in steps]

def inv(notes, n):          # поворот списка
    notes = notes.copy()
    for _ in range(n): notes.append(notes.pop(0))
    return notes

inv_ru  = {"root":"Корень","inv1":"1-е обращение","inv2":"2-е обращение"}
hand_ru = {"RH":"ПР","LH":"ЛР"}

pat = re.compile(
    r"(?P<ch>[A-G][#b]?m?|Bdim)"
    r"_(?P<inv>root|inv1|inv2)"
    r"_(?P<hand>RH|LH)"
    r"-(?P<fin>[\d-]+)(?:\.\w+)?$",                 # расширение опционально
    re.I,
)

rows=[]
with TXT_FILE.open(encoding="utf-8") as f:
    for raw in f:
        s = raw.strip()
        if not s: continue
        m = pat.fullmatch(s)
        if not m:
            print("Пропущена строка:", s); continue

        chord, inv_key, hand_key, fin = m['ch'], m['inv'], m['hand'], m['fin']
        notes = " ".join(inv(triad(chord), {'root':0,'inv1':1,'inv2':2}[inv_key]))

        front = f"{chord} — {inv_ru[inv_key]} ({hand_ru[hand_key]})"
        back  = f"Н: {notes}<br>Аппликатура: {fin} ({hand_ru[hand_key]})"
        rows.append((front, back))

# ── Anki ────────────────────────────────────────────────────────────────
model = genanki.Model(
    2025060715, "TextChord",
    fields=[{"name":"Front"},{"name":"Back"}],
    templates=[{"name":"Card","qfmt":"{{Front}}","afmt":"{{Front}}<hr>{{Back}}"}],
)
deck = genanki.Deck(2025060716, DECK_NAME)
for fr, ba in rows:
    deck.add_note(genanki.Note(model, [fr, ba]))

genanki.Package(deck).write_to_file(APKG_FILE)
print(f"Готово: {APKG_FILE}  |  карточек: {len(rows)}")

