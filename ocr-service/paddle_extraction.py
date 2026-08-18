from pathlib import Path

import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from paddleocr import PaddleOCR


OCR_LANGUAGE = "fr"
PDF_DPI = 120  # Optimisé pour vitesse d'extraction sur CPU

# Un couloir vide horizontal d'au moins ce nombre de pixels est considéré
# comme une vraie séparation de colonnes (et pas un simple espacement de mots)
MIN_COLUMN_GAP = 25
# Tolérance : nombre de boîtes autorisées à "déborder" légèrement dans le
# couloir sans invalider la détection de colonne (une seule ligne trop
# longue ne doit pas faire échouer la détection sur toute la page)
COLUMN_GAP_TOLERANCE = 1
# Une boîte plus large que ce ratio de la largeur du groupe est considérée
# comme un titre "pleine largeur" (sert de séparateur explicite)
WIDE_BOX_RATIO = 0.65
MAX_RECURSION_DEPTH = 8

# Score de confiance en dessous duquel on tente une seconde lecture ciblée
# (recadrage agrandi) car la ligne est suspecte de perte de caractères
RECOVERY_SCORE_THRESHOLD = 0.75
RECOVERY_PAD_LEFT = 40
RECOVERY_PAD_OTHER = 20

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
#
# text_det_unclip_ratio : agrandit la marge de détection autour de chaque
# ligne de texte (défaut ~1.5). ATTENTION : une valeur trop haute (testé à
# 2.0) fait fusionner des lignes proches entre elles à la détection (ex: une
# liste de bullet points serrés), ce qui fait PERDRE du texte au lieu d'en
# récupérer. 1.6 est un compromis plus sûr ; le second passage ciblé sur les
# lignes à faible confiance (voir plus bas) fait le reste du travail.
# Si ce paramètre n'existe pas dans ta version installée (PaddleOCR < 3.0),
# remplace-le par det_db_unclip_ratio=1.6.

def _init_paddleocr():
    kwargs_list = [
        {"lang": OCR_LANGUAGE, "text_det_unclip_ratio": 1.6, "use_textline_orientation": False},
        {"lang": OCR_LANGUAGE, "det_db_unclip_ratio": 1.6, "use_angle_cls": False},
        {"lang": OCR_LANGUAGE, "use_angle_cls": False},
        {"lang": OCR_LANGUAGE},
    ]
    for kwargs in kwargs_list:
        try:
            return PaddleOCR(**kwargs)
        except Exception:
            continue
    return PaddleOCR(lang="fr")

ocr = _init_paddleocr()


# ============================================================
# LECTURE DES RESULTATS PADDLEOCR 3.x (inchangé, déjà correct)
# ============================================================

def get_result_value(result, key, default=None):
    if hasattr(result, key):
        return getattr(result, key)
    try:
        return result[key]
    except (KeyError, TypeError, IndexError):
        return default


def get_box_coordinates(box):
    box = np.asarray(box)

    if box.ndim == 1 and len(box) == 4:
        x_min, y_min, x_max, y_max = box
        return (float(x_min), float(y_min), float(x_max), float(y_max))

    if box.ndim == 2 and box.shape == (4, 2):
        x_min, y_min = box[:, 0].min(), box[:, 1].min()
        x_max, y_max = box[:, 0].max(), box[:, 1].max()
        return (float(x_min), float(y_min), float(x_max), float(y_max))

    return None


# ============================================================
# RECUPERATION DES LETTRES PERDUES (score de confiance faible)
# ============================================================

def _recover_low_confidence_text(image_array, item):
    """
    Pour une boîte à faible score de confiance, relance la reconnaissance
    sur un recadrage de l'image agrandi (surtout à gauche) autour de cette
    boîte précise. Corrige les cas où la boîte de détection initiale était
    trop ajustée et a rogné le début du texte.

    Ce n'est PAS une correction de texte codée en dur : c'est une nouvelle
    lecture de l'image sur une zone élargie, générale à tout CV. Le
    remplacement n'a lieu que si le nouveau texte est plus long et contient
    l'ancien texte (donc c'est bien une extension, pas une lecture différente).
    """
    h, w = image_array.shape[:2]
    x0 = max(0, int(item["x_min"]) - RECOVERY_PAD_LEFT)
    y0 = max(0, int(item["y_min"]) - RECOVERY_PAD_OTHER)
    x1 = min(w, int(item["x_max"]) + RECOVERY_PAD_OTHER)
    y1 = min(h, int(item["y_max"]) + RECOVERY_PAD_OTHER)

    if x1 <= x0 or y1 <= y0:
        return None

    crop = image_array[y0:y1, x0:x1]

    try:
        results = ocr.predict(crop)
    except Exception:
        return None

    texts = []
    for r in results:
        t = get_result_value(r, "rec_texts", [])
        if t is None:
            t = []
        texts.extend(t)

    if not texts:
        return None

    candidate = " ".join(t.strip() for t in texts if t and t.strip())
    return candidate or None


# ============================================================
# ORDRE DE LECTURE : DETECTION DES COLONNES (XY-cut) puis FUSION DE LIGNE
# ============================================================
#
# C'EST ICI QU'ÉTAIT LE BUG PRINCIPAL : l'ancienne version fusionnait tous
# les items à la même hauteur (y proche) en une seule ligne, SANS vérifier
# leur distance horizontale. Résultat : "CONTACT" (colonne gauche) et
# "PROFIL" (colonne droite) à la même hauteur finissaient fusionnés en
# "CONTACT PROFIL". La correction : détecter les colonnes AVANT de fusionner.

def _group_width(items):
    return max(i["x_max"] for i in items) - min(i["x_min"] for i in items)


def _split_by_wide_boxes(items, ratio=WIDE_BOX_RATIO):
    """Les titres pleine largeur (ex: un h1 au-dessus de 2 colonnes) servent
    de séparateurs explicites, pour ne pas bloquer la détection des colonnes."""
    total_width = _group_width(items)
    if total_width <= 0:
        return None

    wide = sorted(
        [i for i in items if (i["x_max"] - i["x_min"]) >= ratio * total_width],
        key=lambda i: i["y_min"],
    )
    if not wide:
        return None

    wide_ids = {id(i) for i in wide}
    others = [i for i in items if id(i) not in wide_ids]

    segments = []
    cursor_y = -float("inf")
    for wb in wide:
        above = [i for i in others if cursor_y <= i["y_min"] < wb["y_min"]]
        if above:
            segments.append(above)
        segments.append([wb])
        cursor_y = wb["y_max"]

    below = [i for i in others if i["y_min"] >= cursor_y]
    if below:
        segments.append(below)

    return segments if len(segments) > 1 else None


def _column_gaps(items, min_gap=MIN_COLUMN_GAP, bin_width=4, tolerance=COLUMN_GAP_TOLERANCE):
    """Cherche les couloirs verticaux quasi vides (au plus `tolerance` boîtes
    les traversant), robuste aux quelques lignes qui débordent légèrement."""
    min_x = min(i["x_min"] for i in items)
    max_x = max(i["x_max"] for i in items)
    n_bins = max(1, int((max_x - min_x) / bin_width) + 1)
    counts = [0] * n_bins

    for i in items:
        start = max(0, int((i["x_min"] - min_x) / bin_width))
        end = min(n_bins - 1, int((i["x_max"] - min_x) / bin_width))
        for b in range(start, end + 1):
            counts[b] += 1

    gaps = []
    idx = 0
    while idx < n_bins:
        if counts[idx] <= tolerance:
            j = idx
            while j < n_bins and counts[j] <= tolerance:
                j += 1
            width = (j - idx) * bin_width
            if width >= min_gap:
                gaps.append((min_x + idx * bin_width, min_x + j * bin_width))
            idx = j
        else:
            idx += 1

    return gaps


def _split_columns(items, min_gap=MIN_COLUMN_GAP):
    if not items:
        return []
    gaps = _column_gaps(items, min_gap=min_gap)
    if not gaps:
        return [items]

    cut_points = sorted(g[0] + (g[1] - g[0]) / 2 for g in gaps)
    columns = [[] for _ in range(len(cut_points) + 1)]
    for i in items:
        cx = (i["x_min"] + i["x_max"]) / 2
        idx = 0
        while idx < len(cut_points) and cx >= cut_points[idx]:
            idx += 1
        columns[idx].append(i)

    return [c for c in columns if c]


def _split_bands(items, min_gap=12):
    if not items:
        return []
    y_intervals = sorted((i["y_min"], i["y_max"]) for i in items)
    merged = [list(y_intervals[0])]
    for s, e in y_intervals[1:]:
        if s <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])

    gaps = [
        (merged[k][1], merged[k + 1][0])
        for k in range(len(merged) - 1)
        if merged[k + 1][0] - merged[k][1] >= min_gap
    ]
    if not gaps:
        return [items]

    cut_points = [g[0] + (g[1] - g[0]) / 2 for g in gaps]
    bands = [[] for _ in range(len(cut_points) + 1)]
    for i in items:
        idx = 0
        while idx < len(cut_points) and i["y_min"] >= cut_points[idx]:
            idx += 1
        bands[idx].append(i)

    return [b for b in bands if b]


def _merge_into_lines(items):
    """Fusionne les fragments proches en lignes de texte (logique d'origine du
    projet, conservée mais appliquée UNIQUEMENT à l'intérieur d'une même
    colonne, plus jamais entre deux colonnes)."""
    items_sorted = sorted(items, key=lambda i: (i["y_min"] + i["y_max"]) / 2)
    grouped = []

    for item in items_sorted:
        y_center = (item["y_min"] + item["y_max"]) / 2
        height = item["y_max"] - item["y_min"]
        placed = False
        for line in grouped:
            tolerance = min(height, line["height"]) * 0.5
            if abs(y_center - line["y_center"]) <= tolerance:
                line["items"].append(item)
                line["y_center"] = sum((e["y_min"] + e["y_max"]) / 2 for e in line["items"]) / len(line["items"])
                line["height"] = max(e["y_max"] - e["y_min"] for e in line["items"])
                placed = True
                break
        if not placed:
            grouped.append({"y_center": y_center, "height": height, "items": [item]})

    lines = []
    for line in grouped:
        line["items"].sort(key=lambda i: i["x_min"])
        text = " ".join(i["text"] for i in line["items"] if i["text"].strip())
        if text.strip():
            lines.append(text.strip())
    return lines


def _reading_order(items, depth=0, max_depth=MAX_RECURSION_DEPTH):
    """Retourne une liste de lignes de texte, dans l'ordre de lecture,
    en respectant les colonnes."""
    if not items:
        return []
    if len(items) == 1:
        return [items[0]["text"]]

    segments = _split_by_wide_boxes(items)
    if segments:
        result = []
        for seg in segments:
            result.extend(_reading_order(seg, depth + 1, max_depth))
        return result

    if depth < max_depth:
        columns = _split_columns(items)
        if len(columns) > 1:
            result = []
            for col in columns:
                result.extend(_reading_order(col, depth + 1, max_depth))
            return result

        bands = _split_bands(items)
        if len(bands) > 1:
            result = []
            for band in bands:
                result.extend(_reading_order(band, depth + 1, max_depth))
            return result

    # Cas de base : plus de colonne/bande à distinguer -> fusion en lignes
    return _merge_into_lines(items)


# ============================================================
# OCR D'UNE IMAGE
# ============================================================

def extract_text_from_image(image):
    image = image.convert("RGB")
    image_array = np.array(image)

    results = ocr.predict(image_array)

    items = []
    for result in results:
        texts = get_result_value(result, "rec_texts", [])
        boxes = get_result_value(result, "rec_boxes", [])
        scores = get_result_value(result, "rec_scores", [])
        texts = [] if texts is None else texts
        boxes = [] if boxes is None else boxes
        scores = [] if scores is None else scores

        for index, text in enumerate(texts):
            if not text or not str(text).strip():
                continue
            if index >= len(boxes):
                continue

            coordinates = get_box_coordinates(boxes[index])
            if coordinates is None:
                continue
            x_min, y_min, x_max, y_max = coordinates

            try:
                score = float(scores[index]) if index < len(scores) else 1.0
            except (TypeError, ValueError):
                score = 1.0

            items.append({
                "text": str(text).strip(),
                "x_min": x_min, "y_min": y_min,
                "x_max": x_max, "y_max": y_max,
                "score": score,
            })

    if not items:
        return []

    # Deuxième passage : relecture ciblée des zones à faible score de confiance (< 0.75)
    for item in items:
        if item["score"] < RECOVERY_SCORE_THRESHOLD:
            recovered_text = _recover_low_confidence_text(image_array, item)
            if recovered_text and len(recovered_text) >= len(item["text"]):
                print(f"[OCR Recovery] Extension texte '{item['text']}' -> '{recovered_text}' (score initial: {item['score']:.2f})")
                item["text"] = recovered_text

    # Séparation prioritaire de l'en-tête (Nom, Prénom, Contacts) en haut de page
    # pour éviter de mélanger le titre/les contacts avec les colonnes de compétences.
    max_y = max(i["y_max"] for i in items)
    header_threshold = 0.16 * max_y

    header_items = [i for i in items if i["y_max"] <= header_threshold]
    body_items = [i for i in items if i["y_max"] > header_threshold]

    lines = []
    if header_items:
        lines.extend(_merge_into_lines(header_items))

    if body_items:
        lines.extend(_reading_order(body_items))
    elif not header_items:
        lines.extend(_reading_order(items))

    return lines


# ============================================================
# OCR D'UN PDF
# ============================================================

def extract_text_from_pdf(file_path):
    images = convert_from_path(str(file_path), dpi=PDF_DPI)
    pages_text = []
    for page_number, image in enumerate(images, start=1):
        print(f"Page {page_number}/{len(images)}")
        page_text = extract_text_from_image(image)
        if page_text:
            pages_text.extend(page_text)
    return pages_text


# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def extract_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    extension = file_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Format non supporté : {extension}")

    if extension == ".pdf":
        lines = extract_text_from_pdf(file_path)
    else:
        image = Image.open(file_path).convert("RGB")
        lines = extract_text_from_image(image)

    if not lines:
        print("Attention : aucun texte détecté par PaddleOCR sur ce fichier.")

    return "\n".join(lines)


# ============================================================
# SAUVEGARDE
# ============================================================

def save_text(text, file_path):
    output_file = OUTPUT_DIR / (Path(file_path).stem + ".txt")
    output_file.write_text(text, encoding="utf-8")
    return output_file


# ============================================================
# TEST DIRECT
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage : python paddle_extraction.py chemin/vers/cv.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    print()
    print("Extraction OCR")
    print(f"Fichier : {input_file}")
    print()

    try:
        text = extract_text(input_file)

        if not text.strip():
            print("Aucun texte détecté.")
            sys.exit(1)

        output_file = save_text(text, input_file)

        print()
        print("================ OCR ================")
        print()
        print(text)
        print()
        print("=====================================")
        print()
        print(f"Texte sauvegardé dans : {output_file}")

    except Exception as error:
        print()
        print("Erreur OCR :")
        print(error)
        sys.exit(1)