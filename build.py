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

shutil.rmtree(builddir)
os.makedirs(builddir)

shutil.copytree("css", os.path.join(builddir, "css"))
shutil.copytree("content/images", os.path.join(builddir, "images"))

'''
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

with open('content/publications.bib') as bibtex_file:
    bibtex_database = bibtexparser.load(bibtex_file)

env = Environment(loader=FileSystemLoader("templates"))
print(env.filters.keys())

def render_to_file(template_filename, output_filename, context):
    template = env.get_template(template_filename)
    with open(os.path.join(builddir, output_filename), "w") as fp:
        fp.write(
            template.render(**context)
        )

render_to_file("publications.html", "publications.html",
               {"this_year": datetime.now().year,
                "pub_list": reversed(sorted(bibtex_database.entries, key=lambda entry: entry["year"]))})

for page in ("about", "cv", "contact"):
    context = publish_parts(source=None, source_class=io.FileInput,
                            source_path="content/%s.rst" % page,
                            writer_name='html',
                            settings_overrides=None)
    context["base_path"] = "."
    render_to_file("general.html", "%s.html" % page, context)


publisher_defaults = dict(source=None, source_class=io.FileInput,
                          destination_path=None,
                          destination_class=io.StringOutput, destination=None,
                          reader=None, reader_name='standalone',
                          parser=None, parser_name='restructuredtext',
                          writer=None, writer_name='html',
                          settings=None, settings_spec=None,
                          settings_overrides=None, config_section=None,
                          enable_exit_status=False)

os.makedirs(os.path.join(builddir, "notes"))
notes = []
for path in os.listdir("content/notes"):
    page, ext = os.path.splitext(path)
    if ext == ".rst":
        #context = publish_parts(source=None, source_class=io.FileInput,
        #                        source_path=os.path.join("content/notes", path),
        #                        writer_name='html',
        #                        settings_overrides=None)
        output, pub = publish_programmatically(
                                source_path=os.path.join("content/notes", path),
                                **publisher_defaults)
        docinfo = pub.document.children[pub.document.first_child_matching_class(nodes.docinfo)]
        date = docinfo.children[docinfo.first_child_matching_class(nodes.date)]
        context = pub.writer.parts
        context['slug'] = page
        context['date'] = date
        notes.append(context)
        context["base_path"] = ".."
        render_to_file("general.html", "notes/%s.html" % page, context)
#import pdb; pdb.set_trace()
render_to_file("notes_index.html", "notes/index.html", {"notes": notes, "base_path": ".."})