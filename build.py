"""
Script to build my homepage.

Usage: build.py [-h] [--server SERVER] command

positional arguments:
  command     either 'build' or 'upload'

optional arguments:
  -h, --help       show this help message and exit
  --server SERVER  host name for upload (e.g. username@example.com)

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
from datetime import datetime, time
from argparse import ArgumentParser
from html.parser import HTMLParser
from jinja2 import FileSystemLoader, Environment
import bibtexparser
from bibtexparser.bparser import BibTexParser
from docutils.core import publish_programmatically
from docutils import io, nodes
from feedgen.feed import FeedGenerator
from pytz import timezone
from sumatra.publishing.sphinxext import sumatra_rst


builddir = "docs"
relative_paths = False
env = Environment(loader=FileSystemLoader("templates"))
publisher_defaults = dict(source=None, source_class=io.FileInput,
                          destination_path=None,
                          destination_class=io.StringOutput, destination=None,
                          reader=None, reader_name='standalone',
                          parser=None, parser_name='restructuredtext',
                          writer=None, writer_name='html',
                          settings=None, settings_spec=None,
                          settings_overrides={
                              'initial_header_level': 3,
                              'sumatra_record_store': "https://labnotebook.andrewdavison.info/records",
                              'sumatra_project': "Destexhe_JCNS_2009",
                              'sumatra_link_icon': "/images/icons/icon_info.png"
                          },
                          config_section=None,
                          enable_exit_status=False)
months = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def render_to_file(template_filename, output_path, context):
    template = env.get_template(template_filename)
    os.makedirs(os.path.join(builddir, output_path), exist_ok=True)
    output_filename = os.path.join(output_path, "index.html")
    with open(os.path.join(builddir, output_filename), "w", encoding='utf-8') as fp:
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
            D['date'] = child.astext()
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


def format_authors(records):
    for record in records:
        authors = record['author'].split(' and ')
        if len(authors) > 1:
            record['author'] = ", ".join(authors[:-1]) + ' and ' + authors[-1]
    return records


def add_ndash(records):
    for record in records:
        if "pages" in record and "--" in record["pages"]:
            record["pages"] = record["pages"].replace("--", "&#8211;")
    return records


def generate_feed(notes):
    nineam = time(9, 0, 0, tzinfo=timezone("Europe/Paris"))
    fg = FeedGenerator()
    fg.id('http://andrewdavison.info/')
    fg.title('Some models are useful')
    fg.link(href='http://andrewdavison.info', rel='alternate')
    fg.subtitle("Andrew Davison's Blog")
    fg.link(href='http://andrewdavison.info/atom.xml', rel='self')
    fg.language('en')
    fg.rights('This blog post is licensed under a Creative Commons Attribution License, CC-BY-3.0. Please feel free to copy or modify it, provided you link to http://andrewdavison.info')
    fg.updated(datetime.now(tz=timezone("Europe/Paris")))

    for note in notes:
        link = "http://andrewdavison.info{base_path}/notes/{page}/".format(**note)
        template = env.get_template("note_feed.xml")
        content = template.render(**note)
        entry = fg.add_entry()
        entry.id(link)
        entry.title(note["title"])
        entry.link(href=link, rel="alternate", type="text/html")
        entry.author(name='Andrew Davison',
                     email='andrew.davison@unic.cnrs-gif.fr')
        entry.content(content, type="xhtml")
        entry.published(datetime.combine(note["date"], nineam))

    fg.atom_file(os.path.join(builddir, 'atom.xml'))
    fg.rss_file(os.path.join(builddir, 'rss.xml'))
    # note: have a Python-specific feed for PlanetSciPy?


def build():

    # -- Remove any existing build directory, and create a new one
    shutil.rmtree(builddir)
    os.makedirs(builddir)

    # -- Copy css, js and image files to build directory
    shutil.copytree("css", os.path.join(builddir, "css"))
    shutil.copytree("js", os.path.join(builddir, "js"))
    for subdir in ("images", "figures", "files", "posters"):
        shutil.copytree("content/%s" % subdir, os.path.join(builddir, subdir))

    # -- Load BibTeX database
    parser = BibTexParser(ignore_nonstandard_types=False)
    with open('content/publications.bib', encoding='utf-8') as bibtex_file:
        article_database = bibtexparser.load(bibtex_file)
    with open('content/presentations.bib', encoding='utf-8') as bibtex_file:
        presentations_database = bibtexparser.load(bibtex_file, parser=parser)

    # -- Create individual BibTeX files
    os.makedirs(os.path.join(builddir, 'publications'), exist_ok=True)
    for article in article_database.entries:
        tmp_db = bibtexparser.bibdatabase.BibDatabase()
        tmp_db.entries = [article]
        # todo: make all relative urls absolute
        directory = os.path.join(builddir, "publications", article["year"])
        if not os.path.exists(directory):
            os.mkdir(directory)
        with open(os.path.join(directory, "%s.bib" % article["ID"]), "w", encoding="utf-8") as fp:
            bibtexparser.dump(tmp_db, fp)

    # -- Build publications page
    print("Building publications page")
    publications = list(reversed(sorted(add_ndash(format_authors(article_database.entries)), key=lambda entry: (entry["year"], months.index(entry["month"])))))
    presentations = list(reversed(sorted((entry for entry in presentations_database.entries if entry["ENTRYTYPE"] != "unpublished"), key=lambda entry: (entry["year"], months.index(entry["month"])))))
    tech_reports = list(reversed(sorted((entry for entry in presentations_database.entries if entry["ENTRYTYPE"] == "unpublished"), key=lambda entry: (entry["year"], months.index(entry["month"])))))
    render_to_file("publications.html", "publications",
                   {"this_year": datetime.now().year,
                    "publications": publications,
                    "presentations": presentations,
                    "tech_reports": tech_reports,
                    "base_path": get_base_path(level=1),
                    "section": "publications"})

    # -- Build simple pages
    print("Building About and CV")
    for page in ("about", "cv"):
        output, pub = publish_programmatically(source_path="content/%s.rst" % page,
                                               **publisher_defaults)
        context = pub.writer.parts
        context["base_path"] = get_base_path(level=1)
        context["section"] = page
        render_to_file("general.html", page, context)

    # -- Build stand-alone pages
    print("Building standalone pages")
    for page in ("jobs", "emploi"):
        output, pub = publish_programmatically(source_path="content/%s.rst" % page,
                                               **publisher_defaults)
        context = pub.writer.parts
        context["base_path"] = get_base_path(level=1)
        context["section"] = page
        render_to_file("standalone.html", page, context)

    # -- Build notes/blog posts
    print("Building blog posts")
    os.makedirs(os.path.join(builddir, "notes"))
    notes = []
    for path in os.listdir("content/notes"):
        page, ext = os.path.splitext(path)
        print("  ", page)
        if ext == ".rst":
            output, pub = publish_programmatically(
                                    source_path=os.path.join("content/notes", path),
                                    **publisher_defaults)
            try:
                docinfo = docinfo_as_dict(pub.document.children[pub.document.first_child_matching_class(nodes.docinfo)])
            except TypeError:
                print("Error")
            else:
                date = datetime.strptime(docinfo["date"], "%Y-%m-%d").date()
                tags = docinfo["tags"]
                #assert docinfo["slug"] == path, "%s != %s" % (docinfo["slug"], page)
                context = pub.writer.parts
                context["page"] = page
                context["date"] = date
                context["date_str"] = date_format(date)
                context["tags"] = tags
                context["base_path"] = get_base_path(level=2)
                context["section"] = "blog"
                notes.append(context)

    notes.sort(key=lambda c: c["date"], reverse=True)
    for context in notes:
        render_to_file("note.html", "notes/%s" % context["page"], context)

    # -- Build index of notes/blog posts
    render_to_file("notes_index.html", "notes", {"notes": notes,
                                                 "base_path": get_base_path(level=1),
                                                 "section": "blog"})

    # -- Build front page
    print("Building index.html")
    render_to_file("index.html", "", {"base_path": get_base_path(level=0),
                                      "notes": notes[:],
                                      "publications": publications[:7],
                                      "presentations": presentations[:4],})

    # -- Generate RSS/Atom feeds
    print("Generating RSS and Atom feeds")
    generate_feed(notes)
    check_links(internal=True, external=False)


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




class LinkParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.internal_links = set()
        self.external_links = set()

    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    if value.startswith("http"):
                        self.external_links.add(value)
                    elif value.startswith("mailto"):
                        pass
                    else:
                        self.internal_links.add(value)


def check_links(internal=True, external=True):
    import requests
    parser = LinkParser()
    for (dirpath, dirnames, filenames) in os.walk(builddir):
        #print(dirpath, dirnames, filenames)
        for filename in filenames:
            base, ext = os.path.splitext(filename)
            if ext == ".html":
                with open(os.path.join(dirpath, filename)) as fp:
                    parser.feed(fp.read())
    if internal:
        for url in parser.internal_links:
            if url[0] == "#":  # internal reference
                continue
            elif url[-1] == "/":  # directory
                filename = os.path.join(builddir, url[1:], "index.html")
            else:
                filename = os.path.join(builddir, url[1:])
            if not os.path.exists(filename):
                print(url, "does not exist")
    if external:
        for url in parser.external_links:
            try:
                response = requests.head(url)
            except Exception:
                print(url, "- error when checking URL")
            else:
                if response.status_code > 400:
                    print(url, "does not exist")
    #print(parser.external_links)
    #print(parser.internal_links)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('command', help="either 'build', 'upload', or 'checklinks'")
    parser.add_argument('--server', help="host name for upload (e.g. username@example.com)")
    args = parser.parse_args()
    if args.command == "build":
        build()
    elif args.command == "upload":
        username, url = args.server.split("@")
        upload(url, username)
    elif args.command == "checklinks":
        check_links()
    else:
        print("No such command")
        sys.exit(1)
