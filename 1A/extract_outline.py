import os
import json
import unicodedata
import pdfplumber
from collections import Counter

def normalize_text(text):
    return unicodedata.normalize("NFKC", text or "").strip()

def detect_title(pdf):
    if not pdf.pages:
        return ""
    page = pdf.pages[0]
    words = page.extract_words(extra_attrs=["size", "top"])
    if not words:
        return ""
    # Sort words by largest font and top position for title candidate
    sorted_words = sorted(words, key=lambda w: (-float(w["size"]), float(w["top"])))
    for w in sorted_words:
        txt = normalize_text(w["text"])
        if len(txt) >= 5 and not txt.isupper():
            return txt
    return normalize_text(sorted_words[0]["text"])

def is_heading_candidate(word):
    txt = normalize_text(word["text"])
    if not txt or len(txt) > 120:
        return False
    if any(ch in txt for ch in ["©", "Table", "Fig", "@"]):
        return False
    # Check for capitalized words or common heading keywords
    if any(w and w[0].isupper() for w in txt.split()):
        return True
    keywords = ["Introduction", "Conclusion", "Summary", "Results", "Discussion"]
    return any(kw.lower() in txt.lower() for kw in keywords)

def assign_heading_levels(words):
    font_sizes = Counter(float(w["size"]) for w in words)
    common_sizes = sorted(font_sizes.keys(), reverse=True)[:3]
    return {size: f"H{i+1}" for i, size in enumerate(common_sizes)}

def extract_outline(pdf):
    candidates = []
    for pageno, page in enumerate(pdf.pages, start=1):
        words = page.extract_words(extra_attrs=["size"])
        for w in words:
            if is_heading_candidate(w):
                w["page"] = pageno
                candidates.append(w)

    if not candidates:
        return []

    level_map = assign_heading_levels(candidates)
    outline = []
    for w in candidates:
        size = float(w["size"])
        level = level_map.get(size)
        if level:
            outline.append({
                "level": level,
                "text": normalize_text(w["text"]),
                "page": w["page"]
            })
    outline.sort(key=lambda x: (x["page"], x["level"]))
    return outline

def process_pdf_file(input_path, output_path):
    with pdfplumber.open(input_path) as pdf:
        title = detect_title(pdf)
        outline = extract_outline(pdf)
        result = {"title": title, "outline": outline}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    for fn in os.listdir(input_dir):
        if fn.lower().endswith(".pdf"):
            process_pdf_file(os.path.join(input_dir, fn), os.path.join(output_dir, fn[:-4] + ".json"))

if __name__ == "__main__":
    main()
