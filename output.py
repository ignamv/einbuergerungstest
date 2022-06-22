"""Generate files for Anki from database"""
import csv
from pathlib import Path
from db import conn


def write_anki():
    """Create images and csv file for import to Anki"""
    outdir = Path("anki")
    imagedir = outdir / "images"
    imagedir.mkdir(exist_ok=True, parents=True)

    csv_fields = [
        "image",
        "bundesland",
        "answer0",
        "answer1",
        "answer2",
        "answer3",
        "correct0",
        "correct1",
        "correct2",
        "correct3",
    ]
    with open(outdir / "questions.csv", "w", encoding="utf8") as fd:
        csvwriter = csv.DictWriter(fd, csv_fields)
        csvwriter.writeheader()
        # fd.write(','.join(csv_fields) + '\n')
        for row in conn.execute("SELECT * FROM questions"):
            rowdict = dict(row)
            # Give general questions a nonempty tag
            if rowdict["bundesland"] is None:
                rowdict["bundesland"] = "Allgemein"
            # Create HTML for Anki card including the image
            id_ = rowdict.pop("id")
            filename = f"einbuergerung_{id_}.png"
            rowdict["image"] = f'<img src="{filename}">'
            # Save image to file
            question_png_bytes = rowdict.pop("question_png_bytes")
            with open(imagedir / filename, "wb") as imagefile:
                imagefile.write(question_png_bytes)
            # Create fields used by Anki card HTML classes to show which answer is correct
            correct_answer_index = rowdict.pop("correct_answer_index")
            for ii in range(4):
                rowdict[f"correct{ii}"] = (
                    "correct" if correct_answer_index == ii else "incorrect"
                )
            csvwriter.writerow(rowdict)


if __name__ == "__main__":
    write_anki()
