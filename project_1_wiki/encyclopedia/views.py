import random

from django.shortcuts import render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    html_content = util.get_entry_html(title)

    if html_content is None:
        return render(request, "encyclopedia/error.html", {
            "error_message": "Page not found."
            })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": title,
            "html_content": html_content
            })


def search(request):
    search_entry = request.GET.get('q').strip()
    html_content = util.get_entry_html(search_entry)

    if html_content is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry": search_entry,
            "html_content": html_content
        })
    else:
        entries = util.list_entries()
        matching_entries = [entry for entry in entries if search_entry.lower() in entry.lower()]        
        return render(request, "encyclopedia/search.html", {
            "search_results": matching_entries
        })


def new_page(request):
    if request.method == "POST":
        title = request.POST.get('title').strip()
        md_content = request.POST.get('md_content')
        entries = [entry.lower() for entry in util.list_entries()]

        if title.lower() in entries:
            return render(request, "encyclopedia/error.html", {
                "error_message": "Page already exists."
            })
        else:
            util.save_entry(title, md_content)
            html_content = util.get_entry_html(title)
            return render(request, "encyclopedia/entry.html", {
                "entry": title,
                "html_content": html_content 
            })
    else:
        return render(request, "encyclopedia/new_page.html")


def edit(request, title):
    if request.method == "POST":
        md_content = request.POST.get('md_content')
        util.save_entry(title, md_content)
        html_content = util.get_entry_html(title)
        return render(request, "encyclopedia/entry.html", {
            "entry": title,
            "html_content": html_content
        })
    else:
        md_content = util.get_entry_markdown(title)
        return render(request, "encyclopedia/edit.html", {
            "entry": title,
            "md_content": md_content
        })


def random_entry(request):
    entries = util.list_entries()
    generate_random_entry = random.choice(entries)
    html_content = util.get_entry_html(generate_random_entry)
    return render(request, "encyclopedia/random_entry.html", {
        "random_entry": generate_random_entry,
        "html_content": html_content
    })
