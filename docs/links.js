"use strict";


function add_header_links()
{
    let style = document.createElement("style");
    style.id = "headerlinks"
    document.head.appendChild(style);
    style.sheet.insertRule(
        "a.headerlink {"           +
        "  visibility: hidden;"    +
        "  text-decoration: none;" +
        "  font-size: 0.8em;"      +
        "  padding: 0 4px 0 4px;"  +
        "}");
    style.sheet.insertRule(
        ":hover > a.headerlink {"  +
        "  visibility: visible;"   +
        "}");

    let headers = document.querySelectorAll("h2, h3, h4, h5, h6");
    for (let i = 0, len = headers.length; i < len; ++i)
    {
        let header = headers[i];

        let id = header.id || header.parentNode.id;
        if (!id)
            continue;

        let link = document.createElement("a");
        link.href = "#" + id;
        link.className = "headerlink";
        link.textContent = "¶";

        header.appendChild(link);
    }
}


if (document.readyState !== "loading") {
    add_header_links();
} else {
    document.addEventListener("DOMContentLoaded", add_header_links);
}
