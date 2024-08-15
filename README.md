# Anki Deck für den deutschen Einbürgerungstest (alle Bundesländer)

Dieses Skript scrapt die Fragen und Antworten für den deutschen Einbürgerungstest von http://oet.bamf.de/ .
Sie werden in einer Sqlite3 Datenbank gespeichert und dann exportiert, um mit Anki zu nutzen.

* [Finale Anki Deck in Ankiweb](https://ankiweb.net/shared/info/1428016787)

* [Finale Anki Deck als .apkg herunterladen](https://github.com/ignamv/einbuergerungstest/releases)

## Usage

### Scraper

Install the requirements (just selenium at the moment)

```
pip install -r requirements.txt
```

Download [geckodriver](https://github.com/mozilla/geckodriver/releases)
and run this script with its directory in the PATH, e.g.

```
env PATH=$HOME/Downloads:$PATH python3 scrape.py
```

If you get an error in Ubuntu about your profile not being accessible,
try setting a TMPDIR:

```
mkdir tmp
env PATH=$HOME/Downloads:$PATH TMPDIR=./tmp python3 scrape.py
```

### Anki writer

This will generate a csv file and a directory with the question images.

```
python3 output.py
```

## Acknowledgements

Thanks to @nikste and @prepor for their contributions!
