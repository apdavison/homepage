"""
Script to build my homepage
"""

'''
create build directory, if it doesn't exist
build front page
    - mostly static
    - build:
        - list of most recent publications
        - list of most recent notes/blog posts
        - list of news items
build publications list
    - from bibtex file
    - lose individual abstract pages? (redirects in webserver conf to abstracts elsewhere online)
build list of notes
    - from reStructuredText files
build individual notes/blog posts
    - from reStructuredText files
copy contact page
    - static. Lose form, just have e-mail address
copy cv
    - static

uploading as separate script? or sub-commands in a single script
based on docutils, pygments, jinja
atom feed?
twitter integration?
files, posters, presentations?
'''

import os
import shutil
from datetime import datetime
from jinja2 import FileSystemLoader, Environment
import bibtexparser
from docutils.core import publish_programmatically, publish_parts
from docutils import io, nodes

builddir = "build"
env = Environment(loader=FileSystemLoader("templates"))
publisher_defaults = dict(source=None, source_class=io.FileInput,
                          destination_path=None,
                          destination_class=io.StringOutput, destination=None,
                          reader=None, reader_name='standalone',
                          parser=None, parser_name='restructuredtext',
                          writer=None, writer_name='html',
                          settings=None, settings_spec=None,
                          settings_overrides={'initial_header_level': 3}, config_section=None,
                          enable_exit_status=False)
months = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

def render_to_file(template_filename, output_filename, context):
    template = env.get_template(template_filename)
    with open(os.path.join(builddir, output_filename), "w") as fp:
        fp.write(template.render(**context))


# -- Remove any existing build directory, and create a new one
shutil.rmtree(builddir)
os.makedirs(builddir)


# -- Copy css and image files to build directory
shutil.copytree("css", os.path.join(builddir, "css"))
shutil.copytree("content/images", os.path.join(builddir, "images"))


# -- Load BibTeX database
with open('content/publications.bib') as bibtex_file:
    article_database = bibtexparser.load(bibtex_file)
with open('content/presentations.bib') as bibtex_file:
    presentations_database = bibtexparser.load(bibtex_file)

# -- Build publications page
publications = list(reversed(sorted(article_database.entries, key=lambda entry: (entry["year"], months.index(entry["month"])))))
presentations = list(reversed(sorted((entry for entry in presentations_database.entries if entry["type"] != "unpublished"), key=lambda entry: (entry["year"], months.index(entry["month"])))))
tech_reports = list(reversed(sorted((entry for entry in presentations_database.entries if entry["type"] == "unpublished"), key=lambda entry: (entry["year"], months.index(entry["month"])))))
render_to_file("publications.html", "publications.html",
               {"this_year": datetime.now().year,
                "publications": publications,
                "presentations": presentations,
                "tech_reports": tech_reports,
                "base_path": ".",
                "section": "publications"})

# -- Build simple pages
for page in ("about", "cv"):
    output, pub = publish_programmatically(source_path="content/%s.rst" % page,
                                           **publisher_defaults)
    context = pub.writer.parts
    context["base_path"] = "."
    context["section"] = page
    render_to_file("general.html", "%s.html" % page, context)

# -- Build notes/blog posts
os.makedirs(os.path.join(builddir, "notes"))
notes = []
for path in os.listdir("content/notes"):
    page, ext = os.path.splitext(path)
    if ext == ".rst":
        output, pub = publish_programmatically(
                                source_path=os.path.join("content/notes", path),
                                **publisher_defaults)
        docinfo = pub.document.children[pub.document.first_child_matching_class(nodes.docinfo)]
        date = docinfo.children[docinfo.first_child_matching_class(nodes.date)].children[0].rawsource
        # tags = ...
        context = pub.writer.parts
        context["page"] = page
        context["date"] = date
        context["base_path"] = ".."
        context["section"] = "notes"
        notes.append(context)

notes.sort(key=lambda c: c["date"], reverse=True)
for context in notes:
        render_to_file("general.html", "notes/%s.html" % context["page"], context)

# -- Build index of notes/blog posts
render_to_file("notes_index.html", "notes/index.html", {"notes": notes, "base_path": ".."})

# -- Build front page
render_to_file("index.html", "index.html", {"base_path": ".",
                                            "notes": notes[:],
                                            "publications": publications[:5]})



'''
Notes on customizing BibTeX import
----------------------------------

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

# Let's define a function to customize our entries.
# It takes a record and return this record.
def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    return record

with open('bibtex.bib') as bibtex_file:
    parser = BibTexParser()
    parser.customization = customizations
    bib_database = bibtexparser.load(bibtex_file, parser=parser)
    print(bib_database.entries)
'''