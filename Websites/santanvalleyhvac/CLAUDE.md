# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Eleventy (11ty) static site generator project for a contractor/construction company website with a dynamic blog system. The site automatically generates blog posts from Markdown files and is configured for deployment on Netlify.

## Essential Commands

```bash
# Install dependencies
npm install

# Start development server (runs on http://localhost:8080)
npm start

# Build static site (outputs to _site directory)
npm run build
```

## Architecture & Key Concepts

### Static Site Generation with Eleventy
- The project uses Eleventy to transform Nunjucks templates (`.njk`) and Markdown files into static HTML
- Blog posts are automatically generated from Markdown files in `src/blog/`
- Templates use the Nunjucks templating engine with layouts defined in `src/_includes/`

### Content Structure
- **Blog Posts**: Markdown files in `src/blog/` with specific frontmatter requirements:
  - `layout: post.njk` (required)
  - `title`, `date`, `author`, `excerpt`, `tags` fields
  - Filename convention: `YYYY-MM-DD-slug-name.md`
- **Site Data**: Company information stored in `src/_data/site.json`
- **Page Templates**: Nunjucks files in `src/` root (index.njk, about.njk, etc.)

### Deployment Configuration
- Netlify deployment is pre-configured via `netlify.toml`
- Build command: `npm run build`
- Publish directory: `_site`
- Node version: 18
- Includes Lighthouse plugin for performance monitoring

### Styling
- All styles are in `src/css/style.css`
- Uses CSS custom properties for theming (colors defined as variables)
- Mobile-responsive design included

### Eleventy Configuration
- Configuration is in `.eleventy.js` which sets:
  - Input directory: `src/`
  - Output directory: `_site/`
  - Includes directory: `src/_includes/`
  - Data directory: `src/_data/`
  - CSS files are copied via passthrough