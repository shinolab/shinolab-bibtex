import difflib
import logging
import pathlib
import sys
from collections.abc import Callable

import bibtexparser
from bibtexparser import Library
from bibtexparser.model import Entry, Field

logging.basicConfig(
    handlers=[logging.FileHandler(filename="summary.log", encoding="utf-8", mode="w")],
    format="%(message)s",
    level=logging.INFO,
)


def is_same_entry(a: Entry, b: Entry):
    def compare_field(key: str, compare: Callable[[Field, Field], bool] | None = None):
        compare_fn = compare or (lambda a, b: a.value == b.value)
        a_field = a.fields_dict.get(key)
        b_field = b.fields_dict.get(key)
        return a_field and b_field and compare_fn(a_field, b_field)

    if compare_field("doi"):
        return True

    if compare_field("title", lambda a, b: a.value.lower() == b.value.lower()):
        return True

    return False


def has_same_entry(base: Library, new: Entry) -> Entry:
    for block in base.blocks:
        match block:
            case Entry() as entry:
                if is_same_entry(entry, new):
                    return entry
            case _:
                pass
    return None


def format_entry(entry: Entry) -> str:
    msg = f"{entry.key} {{"
    for key, value in entry.fields_dict.items():
        msg += f"\n\t{key} = {value.value}"
    msg += "\n}"
    return msg


def normalize_key(entry: Entry) -> str | None:
    key = entry.key
    authors = entry.fields_dict.get("author")
    if not authors:
        sys.stderr.write(f"Missing author field in entry with key {key}\n")
        sys.exit(-1)
    author: str = authors.value.lower().split(" and ")[0].strip()
    if author.startswith("{") and author.endswith("}"):
        last_name = author.replace("{", "").replace("}", "").replace(" ", "_").strip()
    elif "," in author:
        last_name = author.split(",")[0].strip().split(" ")[0].strip()
    else:
        last_name = author.split(" ")[-1].strip()

    title = entry.fields_dict.get("title")
    if not title:
        sys.stderr.write(f"Missing title field in entry with key {key}\n")
        sys.exit(-1)
    short_title = "_".join(title.value.lower().replace(" - ", " ").split(" ")[:3])
    short_title = (
        short_title.replace("{", "").replace("}", "").replace(":", "").replace(",", "")
    )

    year = entry.fields_dict.get("year")

    new_key = (
        f"{last_name}-{year.value}-{short_title}"
        if year
        else f"{last_name}-{short_title}"
    )
    if key != new_key:
        entry.key = new_key
        return key
    else:
        return None


def merge_entry(base: Entry, new: Entry) -> list[Field]:
    for key, field in new.fields_dict.items():
        if key in base.fields_dict:
            base_field = base.fields_dict[key]
            if base_field.value != field.value:
                sys.stderr.write(
                    f"Conflicting field {key}: {base_field.value} vs {field.value}\n"
                )
                sys.stderr.write(format_entry(base) + "\n")
                sys.stderr.write(format_entry(new) + "\n")
                sys.exit(-1)
        else:
            base.set_field(field)
    return base


def merge(base: Library, new: Entry):
    entry = has_same_entry(base, new)
    if entry:
        base_entry = format_entry(entry)
        new = merge_entry(entry, new)
        new_entry = format_entry(new)
        normalize_key(new)
        diff = difflib.ndiff(base_entry.split("\n"), new_entry.split("\n"))
        logging.info("=== UPDATE ===")
        logging.info("\n".join(diff))
        logging.info("==============")
        base.remove(entry)
    else:
        old_key = normalize_key(new)
        logging.info("==== ADD =====")
        added = old_key + " -> " + format_entry(new) if old_key else format_entry(new)
        logging.info("\n".join((" " * 2 + x for x in added.split("\n"))))
        logging.info("==============")
    new.pop("urldate")
    base.add(new)


main_bib_file = (pathlib.Path(__file__).parent / "all.bib").resolve()

if not main_bib_file.exists():
    sys.stderr.write("Do not edit all.bib directly!\n")
    sys.exit(-1)

main_library = bibtexparser.parse_file(main_bib_file)
main_keys = set(x.key for x in main_library.blocks)


def check_all_bib():
    for entry in main_library.entries:
        if normalize_key(entry):
            sys.stderr.write("Do not edit all.bib directly!\n")
            sys.exit(-1)


for arg in sys.argv[1:]:
    file = pathlib.Path(arg).resolve()

    if file == main_bib_file:
        check_all_bib()
    elif file.suffix == ".bib":
        if not file.exists():
            continue

        logging.debug(f"Processing {file}...")
        added_library = bibtexparser.parse_file(file)
        added_keys = set(x.key for x in added_library.blocks)
        for diff in added_keys.difference(main_keys):
            new_entry = added_library.entries_dict[diff]
            if new_entry:
                merge(main_library, new_entry)

        file.unlink()


with open(main_bib_file, mode="w", encoding="utf-8") as f:
    f.writelines(bibtexparser.write_string(main_library))
