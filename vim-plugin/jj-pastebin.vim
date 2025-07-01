" JJ Pastebin Vim Plugin
" Author: JJ
" Version: 1.0
" Description: Vim plugin to paste code to JJ Pastebin service

if exists('g:jj_pastebin_loaded')
    finish
endif
let g:jj_pastebin_loaded = 1

" Default configuration
if !exists('g:jj_pastebin_url')
    let g:jj_pastebin_url = 'http://localhost:8000'
endif

if !exists('g:jj_pastebin_username')
    let g:jj_pastebin_username = ''
endif

if !exists('g:jj_pastebin_password')
    let g:jj_pastebin_password = ''
endif

if !exists('g:jj_pastebin_private_default')
    let g:jj_pastebin_private_default = 0
endif

if !exists('g:jj_pastebin_copy_url')
    let g:jj_pastebin_copy_url = 1
endif

" Language mapping for syntax highlighting
let s:language_map = {
    \ 'vim': 'vim',
    \ 'python': 'python',
    \ 'javascript': 'javascript',
    \ 'typescript': 'typescript',
    \ 'java': 'java',
    \ 'c': 'c',
    \ 'cpp': 'cpp',
    \ 'sh': 'bash',
    \ 'bash': 'bash',
    \ 'zsh': 'bash',
    \ 'fish': 'bash',
    \ 'ruby': 'ruby',
    \ 'go': 'go',
    \ 'rust': 'rust',
    \ 'php': 'php',
    \ 'html': 'html',
    \ 'css': 'css',
    \ 'scss': 'scss',
    \ 'sass': 'sass',
    \ 'json': 'json',
    \ 'xml': 'xml',
    \ 'yaml': 'yaml',
    \ 'yml': 'yaml',
    \ 'toml': 'toml',
    \ 'sql': 'sql',
    \ 'markdown': 'markdown',
    \ 'md': 'markdown',
    \ 'tex': 'latex',
    \ 'latex': 'latex',
    \ 'r': 'r',
    \ 'matlab': 'matlab',
    \ 'lua': 'lua',
    \ 'perl': 'perl',
    \ 'scala': 'scala',
    \ 'swift': 'swift',
    \ 'kotlin': 'kotlin',
    \ 'dart': 'dart',
    \ 'dockerfile': 'dockerfile',
    \ 'makefile': 'makefile',
    \ 'conf': 'ini',
    \ 'ini': 'ini',
    \ 'cfg': 'ini'
    \ }

" Get language from filetype
function! s:GetLanguage()
    let filetype = &filetype
    if empty(filetype)
        let filetype = 'text'
    endif
    return get(s:language_map, filetype, filetype)
endfunction

" Get authentication token
function! s:GetAuthToken()
    if empty(g:jj_pastebin_username) || empty(g:jj_pastebin_password)
        return ''
    endif
    
    let auth_data = {
        \ 'username': g:jj_pastebin_username,
        \ 'password': g:jj_pastebin_password
        \ }
    
    let json_data = json_encode(auth_data)
    let curl_cmd = printf('curl -s -X POST -H "Content-Type: application/json" -d %s %s/api/auth/login',
        \ shellescape(json_data), g:jj_pastebin_url)
    
    let response = system(curl_cmd)
    
    if v:shell_error != 0
        return ''
    endif
    
    try
        let parsed = json_decode(response)
        return get(parsed, 'token', '')
    catch
        return ''
    endtry
endfunction

" Create paste
function! s:CreatePaste(content, title, is_private)
    let language = s:GetLanguage()
    
    let paste_data = {
        \ 'title': a:title,
        \ 'content': a:content,
        \ 'language': language,
        \ 'is_public': a:is_private ? v:false : v:true
        \ }
    
    let json_data = json_encode(paste_data)
    let headers = ['-H "Content-Type: application/json"']
    
    " Add authentication if credentials are provided
    let token = s:GetAuthToken()
    if !empty(token)
        call add(headers, printf('-H "Authorization: Bearer %s"', token))
    endif
    
    let curl_cmd = printf('curl -s -X POST %s -d %s %s/api/pastes',
        \ join(headers, ' '), shellescape(json_data), g:jj_pastebin_url)
    
    let response = system(curl_cmd)
    
    if v:shell_error != 0
        throw "Failed to create paste: curl error"
    endif
    
    try
        let parsed = json_decode(response)
        if has_key(parsed, 'error')
            throw "API Error: " . parsed.error
        endif
        return parsed
    catch
        throw "Failed to parse response: " . response
    endtry
endfunction

" Copy URL to clipboard
function! s:CopyToClipboard(url)
    if g:jj_pastebin_copy_url
        if has('clipboard')
            let @+ = a:url
            let @* = a:url
        elseif executable('pbcopy')
            call system('echo ' . shellescape(a:url) . ' | pbcopy')
        elseif executable('xclip')
            call system('echo ' . shellescape(a:url) . ' | xclip -selection clipboard')
        elseif executable('xsel')
            call system('echo ' . shellescape(a:url) . ' | xsel --clipboard --input')
        endif
    endif
endfunction

" Main paste function
function! s:PasteBin(line1, line2, title, is_private)
    " Get content based on range
    let lines = getline(a:line1, a:line2)
    let content = join(lines, "\n")
    
    if empty(content)
        echo "No content to paste"
        return
    endif
    
    " Generate title if not provided
    let title = a:title
    if empty(title)
        if expand('%') != ''
            let title = expand('%:t')
        else
            let title = 'Untitled'
        endif
        
        " Add line range info if not entire file
        if a:line1 != 1 || a:line2 != line('$')
            let title .= printf(' (lines %d-%d)', a:line1, a:line2)
        endif
    endif
    
    echo "Creating paste..."
    
    try
        let result = s:CreatePaste(content, title, a:is_private)
        let paste_url = g:jj_pastebin_url . '/paste/' . result.unique_id
        
        call s:CopyToClipboard(paste_url)
        
        echo printf("Paste created successfully!")
        echo printf("URL: %s", paste_url)
        echo printf("Title: %s", result.title)
        echo printf("Language: %s", result.language)
        echo printf("Visibility: %s", result.is_public ? "Public" : "Private")
        
        if g:jj_pastebin_copy_url
            echo "URL copied to clipboard!"
        endif
        
    catch
        echohl ErrorMsg
        echo "Error: " . v:exception
        echohl None
    endtry
endfunction

" Command definitions
command! -range=% -nargs=? JJPaste call s:PasteBin(<line1>, <line2>, <q-args>, g:jj_pastebin_private_default)
command! -range=% -nargs=? JJPastePrivate call s:PasteBin(<line1>, <line2>, <q-args>, 1)
command! -range=% -nargs=? JJPastePublic call s:PasteBin(<line1>, <line2>, <q-args>, 0)

" Shorter aliases
command! -range=% -nargs=? JJ call s:PasteBin(<line1>, <line2>, <q-args>, g:jj_pastebin_private_default)
command! -range=% -nargs=? JJPriv call s:PasteBin(<line1>, <line2>, <q-args>, 1)
command! -range=% -nargs=? JJPub call s:PasteBin(<line1>, <line2>, <q-args>, 0)

" Configuration command
command! JJConfig call s:ShowConfig()

function! s:ShowConfig()
    echo "JJ Pastebin Configuration:"
    echo "  URL: " . g:jj_pastebin_url
    echo "  Username: " . (empty(g:jj_pastebin_username) ? "(not set)" : g:jj_pastebin_username)
    echo "  Password: " . (empty(g:jj_pastebin_password) ? "(not set)" : "***")
    echo "  Private by default: " . (g:jj_pastebin_private_default ? "Yes" : "No")
    echo "  Copy URL to clipboard: " . (g:jj_pastebin_copy_url ? "Yes" : "No")
    echo ""
    echo "Usage:"
    echo "  :JJ [title]           - Paste entire buffer"
    echo "  :5,10JJ [title]       - Paste lines 5-10"
    echo "  :'<,'>JJ [title]      - Paste visual selection"
    echo "  :JJPriv [title]       - Create private paste"
    echo "  :JJPub [title]        - Create public paste"
    echo ""
    echo "Configuration (add to .vimrc):"
    echo "  let g:jj_pastebin_url = 'http://localhost:8000'"
    echo "  let g:jj_pastebin_username = 'your_username'"
    echo "  let g:jj_pastebin_password = 'your_password'"
    echo "  let g:jj_pastebin_private_default = 1"
endfunction 