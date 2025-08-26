#!/usr/bin/env node
import React from "react";
import {render} from "ink";
import meow from "meow";
import axios from "axios";
import App from "./app.js";

const MCP_BASE_URL = process.env["MCP_BASE_URL"] ?? "http://localhost:8000";

const cli = meow(
  `
Usage
  $ my-cli jira get --id <TICKET_ID> [--json]

Examples
  $ my-cli jira get --id PROJ-123
  $ MCP_BASE_URL=http://127.0.0.1:8000 my-cli jira get --id PROJ-123 --json
  $ my-cli            (starts interactive REPL)
`,
  {
    importMeta: import.meta,
    flags: {
      id: { type: "string", alias: "i" },
      json: { type: "boolean", default: false }
    }
  }
);

async function runOnce() {
  const [cmd, subcmd] = cli.input;

  if (cmd === "jira" && subcmd === "get") {
    const id = cli.flags.id as string | undefined;
    if (!id) {
      console.error("Error: --id <TICKET_ID> is required");
      process.exit(1);
    }
    try {
      const res = await axios.get(`${MCP_BASE_URL}/jira/${encodeURIComponent(id)}`, { timeout: 10_000 });
      if (cli.flags.json) {
        console.log(JSON.stringify(res.data, null, 2));
      } else {
        const d = res.data as any;
        const lines = [
          `Ticket   : ${d.ticket ?? ""}`,
          `Title    : ${d.title ?? ""}`,
          `Status   : ${d.status ?? ""}`,
          `Assignee : ${d.assignee ?? "-"}`,
          `URL      : ${d.url ?? ""}`,
        ];
        console.log(lines.join("\n"));
      }
    } catch (error: any) {
      const message = error?.response?.data ?? error?.message ?? String(error);
      console.error("Request failed:", message);
      process.exit(1);
    }
    return;
  }

  // Unknown one-shot command -> show help and exit 1
  console.error("Unknown command. Start REPL with: my-cli");
  cli.showHelp(1);
}

async function main() {
  // If any positional args are provided, run in one-shot mode
  if (cli.input.length > 0) {
    await runOnce();
    return;
  }
  // Otherwise start interactive REPL UI
  render(<App />);
}

// eslint-disable-next-line unicorn/prefer-top-level-await
main();