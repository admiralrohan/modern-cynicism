# Modern Cynicism

This repository contains the deployment pipeline for rendering the manuscript via GitHub Pages.

## Deployment Commands

### 1. Run the Script to Format the Manuscript For Markdown

After placing the latest manuscript into the `incoming/` directory, run the processor to wipe old chapters, flatten slugs, and regenerate the table of contents:

```bash
deno task prepare
```

### 2. Preview the Manuscript Locally

To check your layout, formatting, and links locally before updating your site:

```bash
deno task web
```

### 3. Get the PDF of the Manuscript

To generate the PDF of the manuscript, run:

```bash
deno task build
```

### 4. Make Changes to Live Website

After copying the manuscript into the `incoming/` directory and running the processor, you can publish your changes to GitHub Pages:

```bash
deno task deploy
```

(We have github actions setup in this project for automating this process, you just have to push your changes to the main branch)
