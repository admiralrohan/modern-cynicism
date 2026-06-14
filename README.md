# Modern Cynicism

This repository contains the deployment pipeline for rendering the manuscript via GitHub Pages.

## Deployment Commands

### 1. Run the Pipeline

After placing the latest manuscript into the `incoming/` directory, run the processor to wipe old chapters, flatten slugs, and regenerate the table of contents:

```bash
python3 process-manuscript.py
```

### 2. Preview Locally

To check your layout, formatting, and links locally before updating your site:

```bash
quarto preview
```
