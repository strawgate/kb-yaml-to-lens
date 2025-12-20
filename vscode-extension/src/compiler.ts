import { spawn, ChildProcess } from 'child_process';
import * as vscode from 'vscode';
import * as path from 'path';

export class DashboardCompiler {
    private pythonProcess: ChildProcess | null = null;
    private requestId = 0;
    private pendingRequests = new Map<number, {
        resolve: (value: any) => void;
        reject: (error: Error) => void;
    }>();

    constructor(private context: vscode.ExtensionContext) {
        this.startPythonServer();
    }

    private startPythonServer() {
        const config = vscode.workspace.getConfiguration('yamlDashboard');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Find the extension root and the python server script
        const extensionPath = this.context.extensionPath;
        const serverScript = path.join(extensionPath, 'python', 'compile_server.py');

        this.pythonProcess = spawn(pythonPath, [serverScript], {
            cwd: path.join(extensionPath, '..'), // Set cwd to repo root
        });

        if (this.pythonProcess.stdout) {
            let buffer = '';
            this.pythonProcess.stdout.on('data', (data: Buffer) => {
                buffer += data.toString();
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim()) {
                        try {
                            const response = JSON.parse(line);
                            const pending = this.pendingRequests.get(response.id);
                            if (pending) {
                                if (response.success) {
                                    pending.resolve(response.data);
                                } else {
                                    pending.reject(new Error(response.error));
                                }
                                this.pendingRequests.delete(response.id);
                            }
                        } catch (error) {
                            console.error('Failed to parse response:', line, error);
                        }
                    }
                }
            });
        }

        if (this.pythonProcess.stderr) {
            this.pythonProcess.stderr.on('data', (data: Buffer) => {
                console.error('Python server error:', data.toString());
            });
        }

        this.pythonProcess.on('exit', (code) => {
            console.log(`Python server exited with code ${code}`);
            this.pythonProcess = null;
        });
    }

    async compile(filePath: string): Promise<any> {
        if (!this.pythonProcess || !this.pythonProcess.stdin) {
            throw new Error('Python server not running');
        }

        const id = ++this.requestId;
        const request = {
            id,
            method: 'compile',
            params: { path: filePath }
        };

        return new Promise((resolve, reject) => {
            this.pendingRequests.set(id, { resolve, reject });

            if (this.pythonProcess && this.pythonProcess.stdin) {
                this.pythonProcess.stdin.write(JSON.stringify(request) + '\n');
            } else {
                reject(new Error('Python server stdin not available'));
            }

            // Timeout after 30 seconds
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error('Compilation timeout'));
                }
            }, 30000);
        });
    }

    dispose() {
        if (this.pythonProcess) {
            this.pythonProcess.kill();
            this.pythonProcess = null;
        }
        this.pendingRequests.clear();
    }
}
