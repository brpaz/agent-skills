---
name: summarize-article
version: "1.0.0"
description: Given a URL to an article/blog post, fetch its real content, write an actual summary and key takeaways, and save it into an Obsidian vault as a distilled Article note — distinct from a raw Web Clipper capture. Trigger whenever the user pastes an article/blog link and asks to "summarize", "tldr this", "give me the key points", "what's this article about", or similar. Do not use for saving a full verbatim copy of a page — that's what a web-clipper tool already does; this skill produces a distilled summary, not a raw archive.
tags: [obsidian, article, summarization, note-taking, web-clipping]
---

# Summarize Article — content summary into Obsidian

Produces a real summary of an article's *content* and writes it into an Obsidian vault as a distilled `Article` note, separate from a full raw web-clip.

If the target vault already has its own Article note schema (e.g. a Templater template — check somewhere like `99 - Resources/Templater/Templates/Entity/Article.md`), match that instead of the built-in schema below, so the note looks the same whether created by hand or by this skill.

## Workflow

**1. Check for an existing note first.**

```bash
grep -rl "<article-url>" "30 - Collections/Web Clippings/" 2>/dev/null
```

Adjust the search path to wherever the vault archives articles if it isn't this default. If a note for this URL already exists, update its `## Summary` and `## Key Takeaways` sections in place in step 5 rather than creating a duplicate — leave `## Notes` untouched, since it may hold the user's own annotations.

**2. Fetch real metadata — never fabricate it.**

```bash
curl -s -L -A "Mozilla/5.0" "<article-url>" -o "<scratchpad>/article.html"
grep -oP '(?<=property="og:title" content=")[^"]*' "<scratchpad>/article.html" | head -1
grep -oP '(?<=property="og:description" content=")[^"]*' "<scratchpad>/article.html" | head -1
grep -oP '(?<=name="author" content=")[^"]*' "<scratchpad>/article.html" | head -1
grep -oP '(?<=property="article:published_time" content=")[^"]*' "<scratchpad>/article.html" | head -1
```

These give `title`, `description` (→ frontmatter `summary`), `author`, and `published`. Sites vary in which OG/meta tags they set — fall back to the `<title>` tag and a byline search in the body text when a field is missing, and leave a field empty rather than guessing.

**3. Get the actual article text.**

```bash
w3m -dump "<article-url>" > "<scratchpad>/article-text.txt"
```

If `w3m` isn't available, `lynx -dump` or `pandoc -f html -t plain` from the downloaded HTML work as substitutes. If the result is suspiciously short (under ~500 words for what's clearly a full article — JS-rendered page, paywall interstitial, cookie-consent wall), none of those will get through. Fall back to the WebFetch tool with a prompt asking for the complete article text verbatim, and use that instead.

**4. Read the text and write the summary yourself.**

Use the Read tool on `article-text.txt` (or the WebFetch result), then write in your own words — this is a normal reading/synthesis task, not a call to an external summarization API:

- `## Summary` — 3-5 sentences covering the article's core argument/finding and its throughline, not a paragraph-by-paragraph recap.
- `## Key Takeaways` — bullets for the concrete claims, numbers, recommendations, or conclusions a reader would actually want to look back up. Keep these literal, not paraphrased into vagueness.

Skip site chrome, related-article lists, and comment sections that a dump tool sometimes pulls in — read for the actual article body only.

**5. Write or update the note.**

Default folder/filename convention (adjust to match the vault's own if it already has one):

```
30 - Collections/Web Clippings/<YYYY>/<MM>/<Article Title>.md
```

Default frontmatter/body schema:

```yaml
---
Type: Article
summary: <the og:description / meta description from step 2>
url: <article-url>
author:
  - "<author name from step 2, plain text>"
created: <YYYY-MM-DD>
tags:
  - article
---

## Summary

<your summary from step 4>

---

## Key Takeaways

<your bullets from step 4>

---

## Notes


---

## Full Content

> *(Leave as a placeholder unless the full text is explicitly requested alongside the summary.)*


----

## Links
```

Leave `## Notes` empty (reserved for the user) and `## Full Content` as a placeholder — don't dump the full extracted text there by default, since that duplicates what a full web-clip capture already does; only fill it in if the user explicitly asks for the full text alongside the summary.

**6. Verify the URL resolves** before writing it into frontmatter:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "<article-url>"
```

A non-200 is worth flagging to the user, not silently writing anyway.

**7. Report the path back to the user.**
