"""
Minimal Jusu++ Language Server skeleton using pygls.
Run:
  pip install pygls
  python tools/lsp_server.py

Connect from VSCode by configuring the language client to point to this script.
This is intentionally minimal and only handles initialize and didOpen events.
"""
import logging
from pygls.server import LanguageServer
from pygls.features import INITIALIZE, TEXT_DOCUMENT_DID_OPEN
from pygls.types import (InitializeParams, DidOpenTextDocumentParams, Diagnostic, DiagnosticSeverity, Position, Range)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ls = LanguageServer('jusuplusplus', 'v0.1')

@ls.feature(INITIALIZE)
def on_initialize(ls, params: InitializeParams):
    log.info('Jusu++ LSP initialized')

from pygls.types import Diagnostic, DiagnosticSeverity, Range, Position
import re


@ls.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls, params: DidOpenTextDocumentParams):
    uri = params.text_document.uri
    text = params.text_document.text
    log.info(f'Did open: {uri} (len={len(text)})')

    diagnostics = []
    # Try to compile to AST to detect syntax errors
    try:
        from runtime.compiler import compile_to_ast
        compile_to_ast(text)
    except SyntaxError as e:
        # Attempt to extract line number from message like "[Line 3] ..."
        m = re.search(r"\[Line (\d+)\]", str(e))
        line = int(m.group(1)) - 1 if m else 0
        diag = Diagnostic(range=Range(start=Position(line=line, character=0), end=Position(line=line, character=1)), message=str(e), severity=DiagnosticSeverity.Error)
        diagnostics.append(diag)

    ls.publish_diagnostics(uri, diagnostics)

# Also handle text changes to provide live diagnostics
from pygls.features import TEXT_DOCUMENT_DID_CHANGE, TEXT_DOCUMENT_HOVER, COMPLETION
from pygls.types import Hover, MarkupContent, CompletionItem, CompletionItemKind, CompletionList, CompletionParams, HoverParams

@ls.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params):
    uri = params.text_document.uri
    text = params.content_changes[0].text
    diagnostics = []
    try:
        from runtime.compiler import compile_to_ast
        compile_to_ast(text)
    except SyntaxError as e:
        m = re.search(r"\[Line (\d+)\]", str(e))
        line = int(m.group(1)) - 1 if m else 0
        diag = Diagnostic(range=Range(start=Position(line=line, character=0), end=Position(line=line, character=1)), message=str(e), severity=DiagnosticSeverity.Error)
        diagnostics.append(diag)
    ls.publish_diagnostics(uri, diagnostics)


@ls.feature(TEXT_DOCUMENT_HOVER)
def hover(ls, params: HoverParams):
    uri = params.text_document.uri
    pos = params.position
    doc = ls.workspace.get_document(uri)
    line = doc.lines[pos.line]
    # find word at position
    import re
    m = re.search(r"(\w+(?:\.\w+)*)", line)
    if not m:
        return None
    word = m.group(1)

    # check builtins and stdlib
    info = None
    try:
        from runtime import stdlib
        built = stdlib.get_builtins()
    except Exception:
        built = {}

    if word in built:
        info = f"**{word}** — module from stdlib"
    else:
        # keywords and interpreter builtins
        try:
            from runtime.interpreter import Interpreter
            kb = list(Interpreter().builtins.keys())
        except Exception:
            kb = []
        if word in kb:
            info = f"**{word}()** — builtin function"
        elif word in ('if','else','function','return','say'):
            info = f"**{word}** — language keyword"

    if info:
        contents = MarkupContent(kind='markdown', value=info)
        return Hover(contents=contents)
    return None


@ls.feature(COMPLETION)
def completions(ls, params: CompletionParams):
    uri = params.text_document.uri
    # Provide simple completions: keywords, builtins, stdlib names
    keywords = ['say','if','else','for','while','function','return','is','to','in','true','false','null','end']
    try:
        from runtime import stdlib
        built = stdlib.get_builtins()
        stdnames = list(built.keys())
    except Exception:
        stdnames = []
    try:
        from runtime.interpreter import Interpreter
        kb = list(Interpreter().builtins.keys())
    except Exception:
        kb = []

    items = []
    for k in keywords:
        items.append(CompletionItem(label=k, kind=CompletionItemKind.Keyword))
    for k in kb:
        items.append(CompletionItem(label=k+'()', kind=CompletionItemKind.Function))
    for k in stdnames:
        items.append(CompletionItem(label=k, kind=CompletionItemKind.Module))

    return CompletionList(is_incomplete=False, items=items)

if __name__ == '__main__':
    ls.start_io()
