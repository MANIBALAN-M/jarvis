import { checkAgentHealth, resolveApiAuthToken } from './agentApi';

type MessageCallback = (data: any) => void;

class AgentWebSocketClient {
  private socket: WebSocket | null = null;
  private listeners: Set<MessageCallback> = new Set();
  private isConnecting: boolean = false;

  public async connect(url: string = 'ws://127.0.0.1:8765/api/v1/ws') {
    if (this.socket || this.isConnecting) return;
    this.isConnecting = true;

    try {
      let token = await resolveApiAuthToken();
      if (!token) {
        const health = await checkAgentHealth();
        if (health && (health as any).api_auth_token) {
          token = (health as any).api_auth_token;
        }
      }

      if (!token) {
        console.warn('[JARVIS WS] Missing API authentication token. Retrying in 5s...');
        this.isConnecting = false;
        setTimeout(() => this.connect(url), 5000);
        return;
      }

      const fullUrl = url.includes('?')
        ? `${url}&token=${encodeURIComponent(token)}`
        : `${url}?token=${encodeURIComponent(token)}`;

      this.socket = new WebSocket(fullUrl);

      this.socket.onopen = () => {
        this.isConnecting = false;
        console.log('[JARVIS WS] Connected to local agent');
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.listeners.forEach((callback) => callback(data));
        } catch (e) {
          console.error('[JARVIS WS] Error parsing message:', e);
        }
      };

      this.socket.onclose = () => {
        this.socket = null;
        this.isConnecting = false;
        // Auto-reconnect after delay
        setTimeout(() => this.connect(url), 5000);
      };

      this.socket.onerror = (err) => {
        console.warn('[JARVIS WS] Error:', err);
        this.socket?.close();
      };
    } catch (e) {
      this.isConnecting = false;
    }
  }

  public subscribe(callback: MessageCallback): () => void {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  public sendCommand(rawText: string) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ raw_text: rawText }));
    }
  }

  public disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const agentWs = new AgentWebSocketClient();
