from django.shortcuts import render

from markdown2 import Markdown

from . import util

from django.http import HttpResponseRedirect
from django.urls import reverse

import random


def decode(title):
    """
    Encodes Markdown to HTML if the file exists, or returns None
    """
    markdowner = Markdown()
    entry = util.get_entry(title)

    if entry == None:
        return None

    return markdowner.convert(entry)



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    # Get an entry's title and if we have it, then make an HTML file
    entry = decode(title)

    # If there is no such title among entries, return error page
    if entry == None:
        return render(request, "encyclopedia/error.html", {
            "title": "Not Found",
            "message": "The requested entry is not found :("
        })

    # If there is such title - render that entry
    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "title": title
        })


def search(request):
    # Get a search query
    query = request.GET.get("q")

    # If there is no query - return blank page
    if not query:
        message = "an empty query!"
        return render(request, "encyclopedia/search.html", {
            "query": message
        })

    # Trying to get an entry, if the query is among titles
    entry_query = decode(query)

    # If success - render an entry's page
    if entry_query is not None:
        # If we do the following code, we will get "q=query" in the URL with the entry's page
        # return render(request, "encyclopedia/entry.html", {
        #     "entry": entry_query,
        #     "title": query
        # })

        # This version uses redirect and reverse, so in URL there will be the name of an entry
        return HttpResponseRedirect(reverse("entry", kwargs={"title": query}), {
            "entry": entry_query,
            "title": query
            })

    # If we cannot make a title of a query then
    # Get the list of entries
    entries = util.list_entries()

    # Create a list for matches
    matches = []

    # Search for matches between a query and titles, all in lowerCase
    for i in entries:
        if query.lower() in i.lower():
            matches.append(i)

    return render(request, "encyclopedia/search.html", {
        "matches": matches,
        "query": query
    })


def new(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new.html")
    else:
        # Get user's inputs
        title = request.POST["entry_title"]
        text = request.POST["entry_text"]

        # Check for blank inputs
        if not title or text:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries()
            })

        # Check if the entry already exists
        if util.get_entry(title):
            return render(request, "encyclopedia/error.html", {
            "title": "Already exists",
            "message": "The provided entry's title is already exists!"
        })

        # Save a new entry
        util.save_entry(title, text)

        # Make an html-decode
        content = decode(title)

        # Redirect to the new entry
        return HttpResponseRedirect(reverse("entry", kwargs={"title": title}), {
            "entry": content,
            "title": title
            })


def edit(request, title):
    if request.method == "GET":
        # Get an entry by title
        entry = util.get_entry(title)

        # Show this entry 
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "entry": entry
        })

    if request.method == "POST":
        # Get user's input
        content = request.POST["content"]

        # Save the content
        util.save_entry(title, content)

        # Redirect to the entry
        return HttpResponseRedirect(reverse("entry", kwargs={"title": title}), {
            "entry": content,
            "title": title
            })


def random_choice(request):
    # Get the list of entries
    entries = util.list_entries()

    # Chose the random one
    title = random.choice(entries)

    # Convert to HTML
    content = decode(title)

    # Display an entry
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": content
    })