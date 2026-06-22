#!/usr/bin/env python3
import os
import re
import shutil

INCOMING_DIR = "incoming"
LIST_CONTINUATION_INDENT = 3

def extract_first_number(text):
    """Extracts true integers to handle the 1 vs 10 sorting bug properly."""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else float('inf')

def find_folder_rank(folder_path):
    """Infers folder reading order by locating the lowest chapter number inside it."""
    try:
        files = os.listdir(folder_path)
        markdown_files = [f for f in files if f.endswith(('.md', '.qmd'))]
        if not markdown_files:
            return float('inf')
        return min(extract_first_number(f) for f in markdown_files)
    except Exception:
        return float('inf')

def clean_to_slug(text):
    """Transforms raw names into clean, numberless, dash-separated web slugs."""
    name, ext = os.path.splitext(text)
    slug = name.strip().lower()
    slug = re.sub(r'^\d+[-_ ]*', '', slug)   # Strip leading sequence numbers
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Strip special characters
    slug = re.sub(r'[\s_]+', '-', slug)       # Spaces/underscores to dashes
    slug = re.sub(r'-+', '-', slug)           # Collapse duplicate dashes
    return f"{slug}{ext}" if ext else slug

def clean_display_title(text):
    """Generates clean title text for sidebar menus and headings."""
    name, _ = os.path.splitext(text)
    cleaned = re.sub(r'^\d+[-_ ]*', '', name).strip()
    return cleaned.replace("-", " ").replace("_", " ").title()

def process_file_content(file_path, original_filename):
    """
    1. Injects H1 title at the top of the file based on its name.
    2. Fixes Scrivener's escaped list numbers (e.g. \\1. -> 1.).
    3. Normalizes continuation lines to consistent indentation.
    4. Converts standalone bold list text like **1. Point 1:** to 1. **Point 1:**.
    5. Strips redundant inner numbers from list item bold text (e.g., 2. **2. Point 2:** -> 2. **Point 2:**).
    6. Promotes standalone **bold** lines to H2.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines(keepends=True)
        modified_lines = []

        chapter_h1_title = clean_display_title(original_filename)

        while lines and not lines[0].strip():
            lines = lines[1:]
        while lines and lines[0].strip().lower().lstrip('#').strip() == chapter_h1_title.lower():
            lines = lines[1:]
            while lines and not lines[0].strip():
                lines = lines[1:]
        modified_lines.append(f"# {chapter_h1_title}\n\n")

        indent_prefix = ' ' * LIST_CONTINUATION_INDENT

        for i, line in enumerate(lines):
            stripped = line.strip()
            ending = "\r\n" if line.endswith("\r\n") else "\n"

            # Fix Scrivener's escaped list numbers (e.g., \1. -> 1.)
            escaped = re.search(r'\\\d+\.', line)
            if escaped:
                line = re.sub(r'\\\d+\.', lambda m: m.group(0)[1:], line)
                stripped = re.sub(r'\\\d+\.', lambda m: m.group(0)[1:], stripped)

            # Convert standalone bold text that looks like a numbered list item
            # e.g., **1. Point 1:** -> 1. **Point 1:**
            #        **1. Point 1:** more text -> 1. **Point 1:** more text
            bold_list_match = re.match(r'^\*\*(\d+)\.\s+(.*?):\s*\*\*', stripped)
            if bold_list_match:
                num = bold_list_match.group(1)
                text = bold_list_match.group(2)
                rest = stripped[bold_list_match.end():].strip()
                if rest:
                    stripped = f"{num}. **{text}:** {rest}"
                else:
                    stripped = f"{num}. **{text}:**"
                line = stripped + ending

            # Remove redundant inner list number from bold text in list items
            # e.g., 2. **2. Point 2:** -> 2. **Point 2:**
            list_match = re.match(r'^(\d+)\.\s+\*\*\1\.\s+', stripped)
            if list_match:
                stripped = re.sub(r'^(\d+)\.\s+\*\*\1\.\s+', r'\1. **', stripped)
                line = stripped + ending

            # Normalize indentation
            if line.startswith((' ', '\t')):
                line = indent_prefix + stripped + ending

            # Match strictly: line is standalone bold text
            match = None
            if not re.match(r'^\d+\.', stripped):
                match = re.match(r'^\*\*(.*?)\*\*$', stripped)

            if match and match.group(1).strip():
                header_text = match.group(1).strip()
                modified_lines.append(f"## {header_text}{ending}")
            else:
                modified_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(modified_lines)
    except Exception as e:
        print(f"⚠️ Failed to process content modifications for {file_path}: {e}")

def purge_old_iteration():
    """Wipes out previous chapter builds in the root, protecting configuration metadata."""
    print("🧹 Purging old iteration files from root...")
    protected_files = {'index.md', 'process-manuscript.py', 'theme.scss', '_quarto.yml', 'README.md', 'table-of-contents.md', 'chapter-list.yml'}

    for item in os.listdir('.'):
        if os.path.isfile(item) and item.endswith(('.md', '.qmd')):
            if item not in protected_files:
                os.remove(item)
                print(f"   Removed old build file: {item}")

def ensure_workspace():
    """Guarantees index.md and the incoming landing zone directory exist."""
    if not os.path.exists("index.md"):
        with open("index.md", "w", encoding="utf-8") as f:
            f.write('---\ntitle: "Modern Cynicism"\n---\n\n# Introduction {.unnumbered}\n\nWelcome.\n')
    if not os.path.exists(INCOMING_DIR):
        os.makedirs(INCOMING_DIR)

def process_pipeline():
    print("=" * 60)
    print("🚀 RUNNING MANUSCRIPT FLATTENING PIPELINE")
    print("=" * 60)

    ensure_workspace()

    incoming_items = os.listdir(INCOMING_DIR)
    if not incoming_items:
        print(f"ℹ️  '{INCOMING_DIR}/' folder is empty. Drop your Scrivener exports there first.")
        print("=" * 60)
        return

    purge_old_iteration()

    quarto_chapters = [
        "book:",
        "  chapters:",
        "    - index.md",
        "    - table-of-contents.md"
    ]

    toc_content = [
        "# Table of Contents {.unnumbered}",
        ""
    ]

    global_chapter_counter = 1

    sub_dirs = [d for d in incoming_items if os.path.isdir(os.path.join(INCOMING_DIR, d))]
    flat_files = [f for f in incoming_items if os.path.isfile(os.path.join(INCOMING_DIR, f)) and f.endswith(('.md', '.qmd'))]

    # CASE A: Scrivener Exported Folders (Parts are active)
    if sub_dirs:
        print(f"📂 Found {len(sub_dirs)} section folders inside incoming/. Processing...")
        sub_dirs.sort(key=lambda d: find_folder_rank(os.path.join(INCOMING_DIR, d)))

        for directory in sub_dirs:
            dir_full_path = os.path.join(INCOMING_DIR, directory)
            section_title = clean_display_title(directory)

            chapters = [f for f in os.listdir(dir_full_path) if f.endswith(('.md', '.qmd'))]
            if not chapters:
                continue
            chapters.sort(key=extract_first_number)

            quarto_chapters.append(f"    - part: \"{section_title}\"")
            quarto_chapters.append("      chapters:")
            toc_content.append(f"## {section_title}\n")

            for chapter in chapters:
                chapter_title = clean_display_title(chapter)
                clean_file_slug = clean_to_slug(chapter)

                old_file_path = os.path.join(dir_full_path, chapter)
                new_file_path = os.path.join(".", clean_file_slug)

                process_file_content(old_file_path, chapter)
                shutil.move(old_file_path, new_file_path)

                quarto_chapters.append(f"        - {clean_file_slug}")
                web_link = clean_file_slug.replace(".md", ".html").replace(".qmd", ".html")

                toc_content.append(f"{global_chapter_counter}. [{chapter_title}]({web_link})")
                global_chapter_counter += 1

            toc_content.append("")

    # CASE B: Scrivener Exported Flat Files Directly (No Parts)
    elif flat_files:
        print(f"📄 Found {len(flat_files)} flat files inside incoming/. Processing...")
        flat_files.sort(key=extract_first_number)

        for chapter in flat_files:
            chapter_title = clean_display_title(chapter)
            clean_file_slug = clean_to_slug(chapter)

            old_file_path = os.path.join(INCOMING_DIR, chapter)
            new_file_path = os.path.join(".", clean_file_slug)

            process_file_content(old_file_path, chapter)
            shutil.move(old_file_path, new_file_path)

            quarto_chapters.append(f"    - {clean_file_slug}")
            web_link = clean_file_slug.replace(".md", ".html").replace(".qmd", ".html")

            toc_content.append(f"{global_chapter_counter}. [{chapter_title}]({web_link})")
            global_chapter_counter += 1

    # Write structural outputs
    with open("chapter-list.yml", "w", encoding="utf-8") as f:
        f.write("\n".join(quarto_chapters) + "\n")

    with open("table-of-contents.md", "w", encoding="utf-8") as f:
        f.write("\n".join(toc_content) + "\n")

    print("=" * 60)
    print(" Manuscript processing complete.")
    print(f" - {len(quarto_chapters) - 4} chapters processed and moved to root")
    print(" - chapter-list.yml updated")
    print(" - table-of-contents.md generated")
    print("=" * 60)

if __name__ == "__main__":
    process_pipeline()
