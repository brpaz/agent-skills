---
name: summarize-youtube-video
version: "1.0.0"
description: Given a YouTube video URL, pull its transcript (never the video/audio itself), write an actual content summary, and save it into an Obsidian vault as a Youtube Video note. Trigger whenever the user pastes a YouTube link and asks to "summarize", "get the key points", "tldr this video", "what's this video about", or similar. Do not use for just cataloging a watched video with no summary — that's a media-logging skill's job, not this one.
tags: [obsidian, youtube, summarization, note-taking, yt-dlp]
---

# Summarize YouTube Video — transcript-based summary into Obsidian

Produces a real summary of a YouTube video's *content* (not just its metadata) and writes it into an Obsidian vault as a `Youtube Video` note. Requires [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) on `PATH`.

If the target vault already has its own Youtube Video note schema (e.g. from a media-cataloging skill or Templater template), match that instead of the built-in schema below — the goal is one consistent note per video, not a competing format.

## Workflow

**1. Extract the video ID and check for an existing note first.**

```bash
# from any share/watch/shorts URL form
video_id=$(yt-dlp --get-id "<url>")
grep -rl "watch?v=$video_id" "30 - Collections/Media/Youtube/Videos/" 2>/dev/null
```

Adjust the search path to wherever the vault keeps its video notes if it isn't this default. If a note already exists, edit it in place in step 6 instead of creating a new file — a video gets exactly one note.

**2. Fetch real metadata — never fabricate it.**

```bash
yt-dlp --skip-download -j "<url>" > "<scratchpad>/yt-meta.json"
```

Pull `title`, `channel` (or `uploader`), `upload_date` (→ `YYYY-MM-DD`), `duration` (seconds), and `description` from the JSON.

**3. Fetch the transcript — this is the actual input to the summary, not the description.**

Prefer manual (human-written) captions over auto-generated ones when both exist:

```bash
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" --sub-format vtt \
  -o "<scratchpad>/%(id)s" "<url>"
```

Clean the resulting `.vtt` into plain text before reading it:

```bash
sed -E '/^WEBVTT|^Kind:|^Language:|-->/d; s/<[^>]+>//g; /^NOTE/d; /^$/d' "<scratchpad>/<video_id>."*".vtt" \
  | awk '!seen[$0]++' > "<scratchpad>/<video_id>-transcript.txt"
```

`awk '!seen[$0]++'` drops the exact-duplicate lines YouTube's rolling auto-captions produce; skim the result for any remaining near-duplicate fragments before using it — auto-captions can still repeat partial phrases across cue boundaries.

**4. No captions available → stop and say so.**

Do not summarize from the title/description alone and present it as a video summary — that's a fabrication. If `yt-dlp` finds no subtitle track in any language, tell the user directly and ask whether to fall back to audio transcription (`yt-dlp -x --audio-format mp3` piped through a local Whisper install, if one is available) or skip.

**5. Read the transcript and write the summary yourself.**

Use the Read tool on the transcript file, then write a structured summary in your own words — this is a normal reading/synthesis task, not a call to any external summarization API. Structure:

- 2-3 sentence overview of what the video is about and its throughline.
- Key points as bullets, grouped by topic/section if the video covers several distinct ones.
- Any concrete claims, numbers, tools, or recommendations the video makes — these are the parts users come back to look up, keep them literal rather than paraphrased into vagueness.

Skip filler (sponsor reads, intros/outros, repeated calls to subscribe) — a transcript-length summary defeats the purpose.

**6. Write or update the note.**

Default folder/filename convention (adjust to match the vault's own if it already has one):

```
30 - Collections/Media/Youtube/Videos/<YYYY.MM>/<YYYY-MM-DD> VIDEO <Video Title>.md
```

Default frontmatter/body schema:

```yaml
---
created: <ISO 8601 timestamp with offset, e.g. 2025-12-22T22:27:58+00:00>
url: "<https://www.youtube.com/watch?v=VIDEO_ID>"
title: "<Video Title>"
channel: "[[<path to channel note in this vault's convention>/<Channel Name>]]"
published: <YYYY-MM-DD>
duration: "<seconds, as a string>"
Type: "Youtube Video"
tags:
  - "youtube"
---

## About

<iframe width="560" height="315" src="https://www.youtube.com/embed/<VIDEO_ID>" title="<Video Title>" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Description

<Video's own description text, quoted as-is.>

## Summary

<your generated summary from step 5>

## Notes

<leave empty — reserved for the user's own highlights/quotes>

## Transcript

<the cleaned transcript text from step 3>
```

Write `channel` as a wikilink in whatever path style the vault's existing notes already use — don't create the channel note yourself if it doesn't exist, just link to where it would be.

If a note already existed (step 1), only add/replace the `## Summary` section — never overwrite `## Notes`, since that may already hold the user's own annotations.

**7. Report the path back to the user.**
