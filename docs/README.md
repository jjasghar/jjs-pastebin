# JJ Pastebin Documentation Site

This directory contains the GitHub Pages documentation site for JJ Pastebin.

## Pages

- **index.html** - Main landing page with project overview, features, and installation instructions
- **api-docs.html** - Complete REST API documentation with examples
- **cli-tools.html** - CLI tools and Vim plugin documentation

## GitHub Pages Setup

To enable GitHub Pages for this repository:

1. Go to your repository settings on GitHub
2. Navigate to the "Pages" section
3. Set the source to "Deploy from a branch"
4. Select the "main" branch and "/docs" folder
5. Click "Save"

Your documentation site will be available at: https://jjasghar.github.io/jjs-pastebin

## Local Development

To test the documentation locally:

```bash
# Serve the docs folder with a simple HTTP server
cd docs
python -m http.server 8080

# Or use Node.js if you prefer
npx http-server . -p 8080
```

Then visit `http://localhost:8080` to view the documentation.

## Features

- **Responsive Design** - Works on desktop, tablet, and mobile
- **Bootstrap 5** - Modern, clean styling
- **Syntax Highlighting** - Prism.js for code examples
- **Smooth Scrolling** - Enhanced navigation experience
- **Mobile Navigation** - Collapsible menu for mobile devices

## Technologies Used

- HTML5 & CSS3
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Prism.js for syntax highlighting
- Vanilla JavaScript for interactions

## Customization

To customize the documentation:

1. Edit the HTML files directly
2. Modify the CSS variables in the `<style>` sections to change colors/spacing
3. Add new pages by creating additional HTML files
4. Update navigation links in all files to include new pages

## Auto-Deployment

Once GitHub Pages is configured, any changes pushed to the `main` branch will automatically update the live documentation site. 