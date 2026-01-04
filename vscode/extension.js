const path = require('path');
const { workspace, window, commands } = require('vscode');
const { LanguageClient, TransportKind } = require('vscode-languageclient');

let client;

function activate(context) {
    // Path to the Python LSP server script
    const serverModule = context.asAbsolutePath(path.join('..','tools','lsp_server.py'));

    // Server options
    let serverOptions = {
        command: 'python',
        args: [serverModule],
        transport: TransportKind.stdio
    };

    // Client options
    let clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'jusu' }]
    };

    client = new LanguageClient('jusuplusplus', 'Jusu++ Language Server', serverOptions, clientOptions);

    client.start();
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = { activate, deactivate };