"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const child_process_1 = require("child_process");
function activate(context) {
    console.log('晶片Pad與Pin分析器已激活');
    // 註冊分析命令
    let analyzeCommand = vscode.commands.registerCommand('chipAnalyzer.analyze', async (uri) => {
        if (uri) {
            await analyzeChipImage(uri.fsPath);
        }
        else {
            // 如果沒有提供URI，讓用戶選擇文件
            const fileUri = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectFolders: false,
                canSelectMany: false,
                filters: {
                    '圖像文件': ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
                },
                openLabel: '選擇晶片圖像'
            });
            if (fileUri && fileUri[0]) {
                await analyzeChipImage(fileUri[0].fsPath);
            }
        }
    });
    // 註冊查看結果命令
    let viewResultsCommand = vscode.commands.registerCommand('chipAnalyzer.viewResults', async () => {
        await viewAnalysisResults();
    });
    // 註冊導出映射表命令
    let exportMappingCommand = vscode.commands.registerCommand('chipAnalyzer.exportMapping', async () => {
        await exportMappingTable();
    });
    context.subscriptions.push(analyzeCommand, viewResultsCommand, exportMappingCommand);
}
exports.activate = activate;
async function analyzeChipImage(imagePath) {
    const config = vscode.workspace.getConfiguration('chipAnalyzer');
    const pythonPath = config.get('pythonPath', 'python');
    const expectedPads = config.get('expectedPads', 152);
    const expectedPins = config.get('expectedPins', 128);
    // 檢查Python腳本是否存在
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('請先打開一個工作區');
        return;
    }
    const scriptPath = path.join(workspaceFolder.uri.fsPath, 'chip_pad_pin_analyzer.py');
    if (!fs.existsSync(scriptPath)) {
        const createScript = await vscode.window.showWarningMessage('找不到分析腳本，是否要創建？', '創建', '取消');
        if (createScript === '創建') {
            await createAnalysisScript(scriptPath);
        }
        else {
            return;
        }
    }
    // 顯示進度條
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: '正在分析晶片圖像...',
        cancellable: false
    }, async (progress) => {
        progress.report({ increment: 0, message: '啟動分析程序...' });
        return new Promise((resolve, reject) => {
            const command = `"${pythonPath}" "${scriptPath}" --input "${imagePath}" --output "analysis_result.jpg" --mapping "pad_pin_mapping.json"`;
            (0, child_process_1.exec)(command, { cwd: workspaceFolder.uri.fsPath }, (error, stdout, stderr) => {
                if (error) {
                    vscode.window.showErrorMessage(`分析失敗: ${error.message}`);
                    reject(error);
                    return;
                }
                if (stderr) {
                    console.error('stderr:', stderr);
                }
                console.log('stdout:', stdout);
                progress.report({ increment: 100, message: '分析完成' });
                vscode.window.showInformationMessage('晶片分析完成！', '查看結果', '打開輸出文件夾').then(selection => {
                    if (selection === '查看結果') {
                        viewAnalysisResults();
                    }
                    else if (selection === '打開輸出文件夾') {
                        vscode.commands.executeCommand('revealFileInOS', vscode.Uri.file(workspaceFolder.uri.fsPath));
                    }
                });
                resolve();
            });
        });
    });
}
async function viewAnalysisResults() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('請先打開一個工作區');
        return;
    }
    const mappingPath = path.join(workspaceFolder.uri.fsPath, 'pad_pin_mapping.json');
    const vscodeMappingPath = path.join(workspaceFolder.uri.fsPath, 'vscode_mapping.json');
    const resultImagePath = path.join(workspaceFolder.uri.fsPath, 'analysis_result.jpg');
    // 檢查結果文件是否存在
    if (!fs.existsSync(mappingPath) && !fs.existsSync(vscodeMappingPath)) {
        vscode.window.showWarningMessage('找不到分析結果，請先執行分析');
        return;
    }
    // 創建並顯示結果面板
    const panel = vscode.window.createWebviewPanel('chipAnalysisResults', '晶片分析結果', vscode.ViewColumn.One, {
        enableScripts: true,
        localResourceRoots: [workspaceFolder.uri]
    });
    // 讀取結果數據
    let mappingData = {};
    let vscodeData = {};
    if (fs.existsSync(mappingPath)) {
        mappingData = JSON.parse(fs.readFileSync(mappingPath, 'utf8'));
    }
    if (fs.existsSync(vscodeMappingPath)) {
        vscodeData = JSON.parse(fs.readFileSync(vscodeMappingPath, 'utf8'));
    }
    // 生成HTML內容
    panel.webview.html = generateResultsHTML(mappingData, vscodeData, resultImagePath, panel.webview, workspaceFolder.uri);
}
function generateResultsHTML(mappingData, vscodeData, imagePath, webview, workspaceUri) {
    const imageUri = fs.existsSync(imagePath) ?
        webview.asWebviewUri(vscode.Uri.file(imagePath)) : '';
    return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晶片分析結果</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .summary {
            background-color: var(--vscode-editor-selectionBackground);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .summary h2 {
            margin-top: 0;
            color: var(--vscode-textLink-foreground);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background-color: var(--vscode-button-background);
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .image-container {
            text-align: center;
            margin: 30px 0;
        }
        .result-image {
            max-width: 100%;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
        }
        .mapping-table {
            background-color: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            overflow: hidden;
            margin: 20px 0;
        }
        .table-header {
            background-color: var(--vscode-button-background);
            padding: 15px;
            font-weight: bold;
        }
        .table-content {
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
        }
        .mapping-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        .mapping-item:last-child {
            border-bottom: none;
        }
        .pad-pin {
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 晶片Pad與Pin分析結果</h1>
        </div>

        <div class="summary">
            <h2>📊 分析摘要</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">${vscodeData.chip_info?.detected_pads || mappingData.total_pads || 0}</div>
                    <div class="stat-label">檢測到的Pad</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${vscodeData.chip_info?.detected_pins || mappingData.total_pins || 0}</div>
                    <div class="stat-label">檢測到的Pin</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${vscodeData.chip_info?.detected_connections || Object.keys(mappingData.connections || {}).length}</div>
                    <div class="stat-label">連接關係</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${vscodeData.chip_info?.detected_connections ? Math.round(vscodeData.chip_info.detected_connections / Math.min(vscodeData.chip_info.detected_pads, vscodeData.chip_info.detected_pins) * 100) : 0}%</div>
                    <div class="stat-label">完成度</div>
                </div>
            </div>
        </div>

        ${imageUri ? `
        <div class="image-container">
            <h2>🖼️ 視覺化結果</h2>
            <img src="${imageUri}" alt="分析結果圖像" class="result-image">
        </div>
        ` : ''}

        <div class="mapping-table">
            <div class="table-header">
                🔗 Pad與Pin對應關係
            </div>
            <div class="table-content">
                ${generateMappingTable(mappingData.connections || {}, vscodeData.mapping || [])}
            </div>
        </div>
    </div>
</body>
</html>`;
}
function generateMappingTable(connections, vscodeMapping) {
    if (vscodeMapping.length > 0) {
        return vscodeMapping.map(item => `
            <div class="mapping-item">
                <span class="pad-pin">PAD_${item.pad_id}</span>
                <span>→</span>
                <span class="pad-pin">PIN_${item.pin_id}</span>
            </div>
        `).join('');
    }
    else {
        return Object.entries(connections).map(([pad, pin]) => `
            <div class="mapping-item">
                <span class="pad-pin">${pad}</span>
                <span>→</span>
                <span class="pad-pin">${pin}</span>
            </div>
        `).join('');
    }
}
async function exportMappingTable() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('請先打開一個工作區');
        return;
    }
    const mappingPath = path.join(workspaceFolder.uri.fsPath, 'pad_pin_mapping.json');
    if (!fs.existsSync(mappingPath)) {
        vscode.window.showWarningMessage('找不到映射表文件，請先執行分析');
        return;
    }
    const exportUri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file(path.join(workspaceFolder.uri.fsPath, 'exported_mapping.json')),
        filters: {
            'JSON files': ['json'],
            'All files': ['*']
        }
    });
    if (exportUri) {
        try {
            const data = fs.readFileSync(mappingPath);
            fs.writeFileSync(exportUri.fsPath, data);
            vscode.window.showInformationMessage(`映射表已導出到: ${exportUri.fsPath}`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`導出失敗: ${error}`);
        }
    }
}
async function createAnalysisScript(scriptPath) {
    // 這裡可以創建分析腳本的內容
    // 為了簡化，我們只是提示用戶
    vscode.window.showInformationMessage('請將 chip_pad_pin_analyzer.py 腳本放置在工作區根目錄中', '確定');
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map