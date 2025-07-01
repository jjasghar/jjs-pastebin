# JJ Pastebin Vim Plugin

A Vim plugin for seamlessly pasting code snippets to your JJ Pastebin service directly from Vim.

## Features

- 🚀 **Easy pasting**: Paste entire buffers, line ranges, or visual selections
- 🔐 **Authentication support**: Optional login for private pastes and user attribution
- 🎨 **Syntax highlighting**: Automatic language detection based on Vim filetype
- 📋 **Clipboard integration**: Automatically copy paste URLs to clipboard
- ⚙️ **Configurable**: Customizable settings for URL, credentials, and defaults
- 🔒 **Privacy options**: Create public or private pastes
- 🎯 **Multiple commands**: Various commands for different use cases

## Installation

### Manual Installation

1. Copy the plugin file to your Vim plugin directory:
   ```bash
   mkdir -p ~/.vim/plugin ~/.vim/doc
   cp jj-pastebin.vim ~/.vim/plugin/
   cp jj-pastebin.txt ~/.vim/doc/
   ```

2. Reload Vim or restart it

### Using a Plugin Manager

#### vim-plug
```vim
Plug 'path/to/jj-pastebin'
```

#### Vundle
```vim
Plugin 'path/to/jj-pastebin'
```

## Configuration

Add these settings to your `~/.vimrc` file:

```vim
" Configure your pastebin server URL
let g:jj_pastebin_url = 'http://localhost:8000'

" Optional: Set credentials for authenticated pastes
let g:jj_pastebin_username = 'your_username'
let g:jj_pastebin_password = 'your_password'

" Optional: Make pastes private by default (0 = public, 1 = private)
let g:jj_pastebin_private_default = 0

" Optional: Copy URLs to clipboard automatically (1 = yes, 0 = no)
let g:jj_pastebin_copy_url = 1
```

### Optional Key Mappings

```vim
" Quick paste mappings
nnoremap <F5> :JJ<CR>
vnoremap <F6> :JJ<CR>
nnoremap <leader>p :JJPriv<CR>
vnoremap <leader>p :JJPriv<CR>
```

## Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `:JJ [title]` | Paste using default privacy setting |
| `:JJPub [title]` | Create a public paste |
| `:JJPriv [title]` | Create a private paste |
| `:JJConfig` | Show configuration and help |

### Examples

```vim
" Paste entire file
:JJ

" Paste entire file with custom title
:JJ My awesome script

" Paste lines 10-20
:10,20JJ Bug reproduction

" Paste visual selection as private
:'<,'>JJPriv Secret code

" Paste current line
:.JJ Single line fix
```

### Workflow

1. Open a file in Vim
2. Select content (optional) or use entire buffer
3. Run `:JJ` command
4. Get the paste URL (automatically copied to clipboard)
5. Share the URL!

## Language Support

The plugin automatically detects file types and maps them to appropriate syntax highlighting:

- Python, JavaScript, TypeScript, Java, C/C++
- Shell scripts (bash, zsh, fish)
- Web technologies (HTML, CSS, SCSS, JSON, XML)
- Configuration files (YAML, TOML, INI)
- And many more...

## Authentication

The plugin supports both authenticated and anonymous pasting:

- **Anonymous**: Just paste without setting credentials
- **Authenticated**: Set username/password for user attribution and private pastes

## Requirements

- Vim with `curl` available in PATH
- JJ Pastebin server running and accessible
- Optional: `pbcopy` (macOS), `xclip`, or `xsel` (Linux) for clipboard support

## Troubleshooting

### Check Configuration
```vim
:JJConfig
```

### Common Issues

1. **"Failed to create paste: curl error"**
   - Check that your pastebin server is running
   - Verify the URL in `g:jj_pastebin_url`
   - Ensure `curl` is installed and in PATH

2. **"API Error: Invalid credentials"**
   - Check your username and password
   - Ensure the user account exists on the server

3. **No clipboard support**
   - Install `pbcopy` (macOS), `xclip`, or `xsel` (Linux)
   - Or set `let g:jj_pastebin_copy_url = 0` to disable

## License

This plugin is provided as-is for use with JJ Pastebin service.

## Contributing

Feel free to submit issues and feature requests! 