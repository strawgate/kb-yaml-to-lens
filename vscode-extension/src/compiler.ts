import { spawn, ChildProcess } from 'child_process';
import * as vscode from 'vscode';
import * as path from 'path';

// Interface for the compiled dashboard result
// Using unknown since the structure depends on the dashboard configuration
export type CompiledDashboard = unknown;

interface PendingRequest {
    resolve: (value: CompiledDashboard) => void;
    reject: (error: Error) => void;
}

export class DashboardCompiler {
    private pythonProcess: ChildProcess | null = null;
    private requestId = 0;
    private pendingRequests = new Map<number, PendingRequest>();

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
            // Reject all pending requests
            for (const pending of this.pendingRequests.values()) {
                pending.reject(new Error('Python server exited unexpectedly'));
            }
            this.pendingRequests.clear();
        });
    }

    async compile(filePath: string): Promise<CompiledDashboard> {
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
            // Setup timeout timer that will be cleared on success/failure
            const timeoutId = setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error('Compilation timeout'));
                }
            }, 30000);

            // Wrap resolve/reject to clear timeout
            const wrappedResolve = (value: CompiledDashboard) => {
                clearTimeout(timeoutId);
                resolve(value);
            };

            const wrappedReject = (error: Error) => {
                clearTimeout(timeoutId);
                reject(error);
            };

            this.pendingRequests.set(id, { resolve: wrappedResolve, reject: wrappedReject });

            if (this.pythonProcess && this.pythonProcess.stdin) {
                try {
                    this.pythonProcess.stdin.write(JSON.stringify(request) + '\n');
                } catch (error) {
                    clearTimeout(timeoutId);
                    this.pendingRequests.delete(id);
                    reject(new Error(`Failed to write to Python server: ${error instanceof Error ? error.message : String(error)}`));
                }
            } else {
                clearTimeout(timeoutId);
                this.pendingRequests.delete(id);
                reject(new Error('Python server stdin not available'));
            }
        });
    }

    dispose() {
        if (this.pythonProcess) {
            this.pythonProcess.kill();
            this.pythonProcess = null;
        }
        // Reject all pending requests before clearing
        for (const pending of this.pendingRequests.values()) {
            pending.reject(new Error('Compiler disposed'));
        }
        this.pendingRequests.clear();
    }
}
