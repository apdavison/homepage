"""
Script to build my homepage.

Usage: build.py [-h] [--url URL] command

positional arguments:
  command     either 'build' or 'upload'

optional arguments:
  -h, --help  show this help message and exit
  --url URL   url for upload

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
import sys
import shutil
from getpass import getpass
from datetime import datetime
from argparse import ArgumentParser
from jinja2 import FileSystemLoader, Environment
import bibtexparser
from docutils.core import publish_programmatically
from docutils import io, nodes


builddir = "build"
relative_paths = False
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

def render_to_file(template_filename, output_path, context):
    template = env.get_template(template_filename)
    os.makedirs(os.path.join(builddir, output_path), exist_ok=True)
    output_filename = os.path.join(output_path, "index.html")
    with open(os.path.join(builddir, output_filename), "w") as fp:
        fp.write(template.render(**context))


def date_format(date):
    def suffix(day):
        "English ordinal suffix for the day of the month, 2 characters; i.e. 'st', 'nd', 'rd' or 'th'"
        if day in (11, 12, 13):  # Special case
            return 'th'
        last = day % 10
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(last, 'th')
    date_str = date.strftime("%d_ %B %Y").replace("_", suffix(date.day))
    if date_str[0] == "0":
        date_str = date_str[1:]
    return date_str


def docinfo_as_dict(docinfo):
    D = {}
    for child in docinfo.children:
        if isinstance(child, nodes.date):
            D['date'] = child.children[0].rawsource
        elif isinstance(child, nodes.author):
            pass  # todo
        elif isinstance(child, nodes.field):
            D[child.children[0].rawsource] = child.children[1].rawsource
        else:
            raise NotImplementedError(str(type(child)))
    return D


def get_base_path(level):
    if relative_paths:
        if level == 0:
            return "."
        if level == 1:
            return ".."
        elif level == 2:
            return "../.."
        else:
            raise NotImplementedError
    else:
        return ""


def build():

    # -- Remove any existing build directory, and create a new one
    shutil.rmtree(builddir)
    os.makedirs(builddir)

    # -- Copy css and image files to build directory
    shutil.copytree("css", os.path.join(builddir, "css"))
    for subdir in ("images", "figures", "files", "posters"):
        shutil.copytree("content/%s" % subdir, os.path.join(builddir, subdir))

    # -- Load BibTeX database
    with open('content/publications.bib') as bibtex_file:
        article_database = bibtexparser.load(bibtex_file)
    with open('content/presentations.bib') as bibtex_file:
        presentations_database = bibtexparser.load(bibtex_file)

    # -- Build publications page
    publications = list(reversed(sorted(article_database.entries, key=lambda entry: (entry["year"], months.index(entry["month"])))))
    presentations = list(reversed(sorted((entry for entry in presentations_database.entries if entry["type"] != "unpublished"), key=lambda entry: (entry["year"], months.index(entry["month"])))))
    tech_reports = list(reversed(sorted((entry for entry in presentations_database.entries if entry["type"] == "unpublished"), key=lambda entry: (entry["year"], months.index(entry["month"])))))
    render_to_file("publications.html", "publications",
                   {"this_year": datetime.now().year,
                    "publications": publications,
                    "presentations": presentations,
                    "tech_reports": tech_reports,
                    "base_path": get_base_path(level=1),
                    "section": "publications"})

    # -- Create individual BibTeX files
    for article in article_database.entries:
        tmp_db = bibtexparser.bibdatabase.BibDatabase()
        tmp_db.entries = [article]
        # todo: make all relative urls absolute
        directory = os.path.join(builddir, "publications", article["year"])
        if not os.path.exists(directory):
            os.mkdir(directory)
        with open(os.path.join(directory, "%s.bib" % article["id"]), "w") as fp:
            bibtexparser.dump(tmp_db, fp)

    # -- Build simple pages
    for page in ("about", "cv"):
        output, pub = publish_programmatically(source_path="content/%s.rst" % page,
                                               **publisher_defaults)
        context = pub.writer.parts
        context["base_path"] = get_base_path(level=1)
        context["section"] = page
        render_to_file("general.html", page, context)

    # -- Build notes/blog posts
    os.makedirs(os.path.join(builddir, "notes"))
    notes = []
    for path in os.listdir("content/notes"):
        page, ext = os.path.splitext(path)
        if ext == ".rst":
            output, pub = publish_programmatically(
                                    source_path=os.path.join("content/notes", path),
                                    **publisher_defaults)
            docinfo = docinfo_as_dict(pub.document.children[pub.document.first_child_matching_class(nodes.docinfo)])
            date = datetime.strptime(docinfo["date"], "%Y-%m-%d").date()
            tags = docinfo["tags"]
            #assert docinfo["slug"] == path, "%s != %s" % (docinfo["slug"], page)
            context = pub.writer.parts
            context["page"] = page
            context["date"] = date
            context["date_str"] = date_format(date)
            context["tags"] = tags
            context["base_path"] = get_base_path(level=2)
            notes.append(context)

    notes.sort(key=lambda c: c["date"], reverse=True)
    for context in notes:
            render_to_file("note.html", "notes/%s" % context["page"], context)

    # -- Build index of notes/blog posts
    render_to_file("notes_index.html", "notes", {"notes": notes,
                                                 "base_path": get_base_path(level=1)})

    # -- Build front page
    render_to_file("index.html", "", {"base_path": get_base_path(level=0),
                                      "notes": notes[:],
                                      "publications": publications[:7],
                                      "presentations": presentations[:4],})


def remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    err = stderr.read()
    if err:
        print(err)
        sys.exit(1)


def upload(url, username, target_dir="webapps/homepage", backup_dir="backups"):
    import paramiko
    import shutil

    shutil.make_archive("homepage", 'zip', builddir)

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    password = getpass("password: ")
    ssh.connect(url, username=username, password=password)

    print("Uploading zipfile")
    sftp = ssh.open_sftp()
    sftp.put('homepage.zip', 'homepage.zip')
    sftp.close()
    os.remove('homepage.zip')

    print("Making backup of current site")
    timestamp = datetime.now().isoformat()
    remote_command(ssh, "cp -r %s %s/homepage_%s" % (target_dir, backup_dir, timestamp))

    print("Removing current site")
    remote_command(ssh, "rm -rf  %s/*; rm -rf %s/.DS_Store" % (target_dir, target_dir))

    print("Unzipping new site")
    remote_command(ssh, "unzip homepage.zip -d %s" % target_dir)

    print("Removing zip file")
    remote_command(ssh, "rm -f homepage.zip")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('command', help="either 'build' or 'upload'")
    parser.add_argument('--url', help="url for upload")
    args = parser.parse_args()
    if args.command == "build":
        build()
    elif args.command == "upload":
        username, url = args.url.split("@")
        upload(url, username)
    else:
        print("No such command")
        sys.exit(1)


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