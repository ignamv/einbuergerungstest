#!/usr/bin/env python3

"""Generate files for Anki from database"""
import csv
import genanki
from pathlib import Path
from db import conn
import textwrap
from datetime import datetime

def write_anki():
    outdir = Path("anki")
    imagedir = outdir / "images"
    imagedir.mkdir(exist_ok=True, parents=True)

    # Define the Anki model
    model_id = 1607392319  # Random unique ID

    fields = [
        {"name": "Image"},
        {"name": "Bundesland"},
        {"name": "Answer0"},
        {"name": "Answer1"},
        {"name": "Answer2"},
        {"name": "Answer3"},
        {"name": "Correct0"},
        {"name": "Correct1"},
        {"name": "Correct2"},
        {"name": "Correct3"},
    ]

    css = textwrap.dedent("""
        .correct {
            color: green;
            font-weight: bold;
        }
        .incorrect {
            color: red;
            text-decoration: line-through;
        }
        .option {
            color: black;
            font-weight: medium;
        }
        ol {
            padding-left: 20px;
        }
        li {
            margin-bottom: 5px;
        }
    """)

    afmt = textwrap.dedent("""
        <div>{{Image}}</div>
        <div>{{Bundesland}}</div>
        <ol>
            <li class="{{Correct0}}">{{Answer0}}</li>
            <li class="{{Correct1}}">{{Answer1}}</li>
            <li class="{{Correct2}}">{{Answer2}}</li>
            <li class="{{Correct3}}">{{Answer3}}</li>
        </ol>
    """)

    qfmt = textwrap.dedent("""
        <div>{{Image}}</div>
        <div>{{Bundesland}}</div>
        <ol>
            <li class="option">{{Answer0}}</li>
            <li class="option">{{Answer1}}</li>
            <li class="option">{{Answer2}}</li>
            <li class="option">{{Answer3}}</li>
        </ol>
    """)

    templates = [
        {
            "name": "Card Template",
            "qfmt": qfmt,
            "afmt": afmt,
        },
    ]

    model = genanki.Model(
        model_id, "Einbürgerung Quiz Model", templates=templates, fields=fields, css=css
    )

    # Create the Anki deck


    deck_id = 2059400110  # Random unique ID
    deck = genanki.Deck(deck_id, "Einbürgerung Quiz")


    # Add notes to the deck
    for row in conn.execute("SELECT * FROM questions"):
        rowdict = dict(row)

        # Assign "Allgemein" if "bundesland" is None
        bundesland = rowdict.get("bundesland")
        if bundesland is None:
            bundesland = "Allgemein"

        # Process the image
        id_ = rowdict["id"]
        filename = f"einbuergerung_{id_}.png"
        question_png_bytes = rowdict["question_png_bytes"]
        with open(imagedir / filename, "wb") as imagefile:
            imagefile.write(question_png_bytes)

        # Identify the correct answer
        correct_answer_index = rowdict["correct_answer_index"]
        correct_classes = [
            "correct" if correct_answer_index == ii else "incorrect" for ii in range(4)
        ]

        # Add a note to the deck
        note = genanki.Note(
            model=model,
            fields=[
                f'<img src="{filename}">',
                bundesland,
                rowdict["answer0"],
                rowdict["answer1"],
                rowdict["answer2"],
                rowdict["answer3"],
                correct_classes[0],
                correct_classes[1],
                correct_classes[2],
                correct_classes[3],
            ],
            tags=[f"Einbürgerung-{bundesland}"],
        )
        deck.add_note(note)

    # Save the Anki package
    package = genanki.Package(deck)
    package.media_files = [str(f) for f in imagedir.iterdir()]

    # Get the current date
    current_date = datetime.now()
    current_date = current_date.strftime("%Y-%m-%d")
    
    package.write_to_file(outdir / f"einbuergerung-quiz-{current_date}.apkg")

    print("Anki package created successfully.")

if __name__ == "__main__":
    write_anki()
