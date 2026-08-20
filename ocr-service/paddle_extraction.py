from pathlib import Path

import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from paddleocr import PaddleOCR


# configuration

OCR_LANGUAGE = "fr"
PDF_DPI = 300

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".pdf"
}


# initialisation OCR

ocr = PaddleOCR(
    lang=OCR_LANGUAGE
)


# lecture du résultat PaddleOCR

def get_result_value(result, key, default=None):
    """
    Récupère une valeur depuis un résultat PaddleOCR 3.x.
    """

    if hasattr(result, key):
        return getattr(result, key)

    try:
        return result[key]
    except (KeyError, TypeError, IndexError):
        return default


# conversion des coordonnées

def get_box_coordinates(box):
    """
    Transforme une boîte PaddleOCR en :

    x_min, y_min, x_max, y_max
    """

    box = np.asarray(box)

    if box.ndim == 1 and len(box) == 4:
        x_min, y_min, x_max, y_max = box

        return (
            float(x_min),
            float(y_min),
            float(x_max),
            float(y_max)
        )

    if box.ndim == 2 and box.shape == (4, 2):
        x_min = box[:, 0].min()
        y_min = box[:, 1].min()
        x_max = box[:, 0].max()
        y_max = box[:, 1].max()

        return (
            float(x_min),
            float(y_min),
            float(x_max),
            float(y_max)
        )

    return None


# réorganisation du texte

def reorder_lines(lines):
    """
    Réorganise les résultats OCR selon leur position
    verticale puis horizontale.
    """

    if not lines:
        return []

    lines = sorted(
        lines,
        key=lambda item: (
            item["y_center"],
            item["x_min"]
        )
    )

    grouped_lines = []

    for item in lines:

        added = False

        for line in grouped_lines:

            tolerance = min(
                item["height"],
                line["height"]
            ) * 0.5

            if abs(
                item["y_center"] - line["y_center"]
            ) <= tolerance:

                line["items"].append(item)

                line["y_center"] = sum(
                    element["y_center"]
                    for element in line["items"]
                ) / len(line["items"])

                line["height"] = max(
                    element["height"]
                    for element in line["items"]
                )

                added = True
                break

        if not added:

            grouped_lines.append(
                {
                    "y_center": item["y_center"],
                    "height": item["height"],
                    "items": [item]
                }
            )

    ordered_text = []

    for line in grouped_lines:

        line["items"].sort(
            key=lambda item: item["x_min"]
        )

        text = " ".join(
            item["text"]
            for item in line["items"]
            if item["text"].strip()
        )

        if text.strip():
            ordered_text.append(
                text.strip()
            )

    return ordered_text


# extraction d'une page PDF

def extract_text_from_image(image):
    """
    Extrait le texte d'une page PDF convertie en image
    avec PaddleOCR.
    """

    image = image.convert("RGB")

    image_array = np.array(image)

    results = ocr.predict(
        image_array
    )

    lines = []

    for result in results:

        texts = get_result_value(
            result,
            "rec_texts",
            []
        )

        boxes = get_result_value(
            result,
            "rec_boxes",
            []
        )

        scores = get_result_value(
            result,
            "rec_scores",
            []
        )

        if texts is None:
            texts = []

        if boxes is None:
            boxes = []

        if scores is None:
            scores = []

        for index, text in enumerate(texts):

            if not text:
                continue

            text = str(text).strip()

            if not text:
                continue

            if index >= len(boxes):
                continue

            coordinates = get_box_coordinates(
                boxes[index]
            )

            if coordinates is None:
                continue

            x_min, y_min, x_max, y_max = coordinates

            height = max(
                y_max - y_min,
                1
            )

            score = 1.0

            if index < len(scores):

                try:
                    score = float(
                        scores[index]
                    )

                except (
                    TypeError,
                    ValueError
                ):
                    score = 1.0

            lines.append(
                {
                    "text": text,
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                    "y_center": (y_min + y_max) / 2,
                    "height": height,
                    "score": score
                }
            )

    return reorder_lines(lines)


# extraction d'un PDF

def extract_text_from_pdf(file_path):
    """
    Convertit chaque page du PDF en image
    puis applique PaddleOCR.
    """

    images = convert_from_path(
        str(file_path),
        dpi=PDF_DPI
    )

    pages_text = []

    for page_number, image in enumerate(
        images,
        start=1
    ):

        print(
            f"Page {page_number}/{len(images)}"
        )

        page_text = extract_text_from_image(
            image
        )

        if page_text:
            pages_text.extend(
                page_text
            )

    return pages_text


# extraction principale

def extract_text(file_path):
    """
    Fonction principale.

    Seuls les fichiers PDF sont acceptés.
    """

    file_path = Path(file_path)

    if not file_path.exists():

        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            f"Format non supporté : {extension}. "
            f"Seuls les fichiers PDF sont acceptés."
        )

    lines = extract_text_from_pdf(
        file_path
    )

    return "\n".join(lines)


# sauvegarde du texte

def save_text(text, file_path):
    """
    Sauvegarde le texte OCR dans output/.
    """

    output_file = OUTPUT_DIR / (
        Path(file_path).stem + ".txt"
    )

    output_file.write_text(
        text,
        encoding="utf-8"
    )

    return output_file


# programme principal

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print(
            "Usage : python paddle_extraction.py chemin/vers/cv.pdf"
        )

        sys.exit(1)

    input_file = sys.argv[1]

    print()
    print("Extraction OCR")
    print(f"Fichier : {input_file}")
    print()

    try:

        text = extract_text(
            input_file
        )

        if not text.strip():

            print(
                "Aucun texte détecté."
            )

            sys.exit(1)

        output_file = save_text(
            text,
            input_file
        )

        print()
        print("================ OCR ================")
        print()
        print(text)
        print()
        print("=====================================")
        print()
        print(
            f"Texte sauvegardé dans : {output_file}"
        )

    except Exception as error:

        print()
        print("Erreur OCR :")
        print(error)

        sys.exit(1)