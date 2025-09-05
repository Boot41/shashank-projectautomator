export type AgentRequest = {
  prompt: string;
  context?: Record<string, unknown>;
  session_id?: string;
};

export type AgentResponse = {
  result?: unknown;
  toolCalls?: Array<{ name: string; args: Record<string, unknown> }>;
  model_summary?: string | null;
  error?: string;
  adk_disabled?: boolean;
  detail?: string;
};

export async function callAgent(
  baseUrl: string,
  req: AgentRequest,
  apiKey?: string,
  timeoutMs = 20000
): Promise<AgentResponse> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    // Prepare request body with session_id if provided
    const requestBody: any = { prompt: req.prompt };
    if (req.context) {
      requestBody.context = req.context;
    }
    if (req.session_id) {
      requestBody.session_id = req.session_id;
    }
    
    const res = await fetch(`${baseUrl.replace(/\/$/, "")}/adk/agent`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-Key": apiKey } : {}),
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });

    const text = await res.text();
    let data: AgentResponse;
    try {
      data = JSON.parse(text);
    } catch (e) {
      throw new Error(`Invalid JSON from agent: ${text}`);
    }
    if (!res.ok) {
      const err = (data && (data as any).detail) || data.error || res.statusText;
      throw new Error(`Agent error ${res.status}: ${err}`);
    }
    return data;
  } finally {
    clearTimeout(id);
  }
}


