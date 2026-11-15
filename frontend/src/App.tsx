import { FormEvent, useMemo, useState } from "react";
import { useStream } from "@langchain/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import TodoList, { type TodoItem } from "./TodoList";
import ThinkingBlock from "./ThinkingBlock";
import ToolCallCard, { type ToolCard } from "./ToolCallCard";
import { task1Prompt, task1Prose, task1Todo, task1Tool } from "./task1Translations";

type RawToolCall = { id?: string; name?: string; args?: unknown };
type Message = {
  id?: string;
  type: string;
  content: unknown;
  tool_calls?: RawToolCall[];
  tool_call_id?: string;
  name?: string;
};
type StreamState = {
  messages: Message[];
  todos?: TodoItem[];
};

const PLAN_MARKERS = ["SESSION INTENT", "SUMMARY", "NEXT STEPS", "ARTIFACTS"];

function messageText(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((part) =>
        typeof part === "string"
          ? part
          : typeof part === "object" && part !== null && "text" in part
            ? String((part as { text: unknown }).text ?? "")
            : "",
      )
      .join("");
  }
  return "";
}

// Walk all messages in stream order, producing a flat list of "rows" to render.
// A row is either a human/ai prose message, an open or completed tool card
// (matched to its tool_call_id), or nothing (a tool message that's been folded
// into its card).
type Row =
  | { kind: "prose"; key: string; type: "human" | "ai"; body: string }
  | { kind: "plan"; key: string; body: string }
  | { kind: "card"; key: string; card: ToolCard };

function isPlanLikeBody(body: string): boolean {
  const normalized = body.toUpperCase();
  const markerHits = PLAN_MARKERS.filter((marker) => normalized.includes(marker)).length;
  return markerHits >= 2 || (markerHits >= 1 && /the user requested/i.test(body));
}

function buildRows(messages: Message[]): Row[] {
  const rows: Row[] = [];
  const cardByCallId = new Map<string, ToolCard>();
  for (const msg of messages) {
    if (msg.type === "human") {
      rows.push({
        kind: "prose",
        key: msg.id ?? `h-${rows.length}`,
        type: "human",
        body: messageText(msg.content),
      });
    } else if (msg.type === "ai") {
      const calls = msg.tool_calls ?? [];
      const body = messageText(msg.content);
      const trimmedBody = body.trim();
      if (trimmedBody) {
        if (isPlanLikeBody(trimmedBody)) {
          rows.push({ kind: "plan", key: msg.id ?? `p-${rows.length}`, body: trimmedBody });
        } else {
          rows.push({
            kind: "prose",
            key: msg.id ?? `a-${rows.length}`,
            type: "ai",
            body: trimmedBody,
          });
        }
      }
      if (calls.length > 0) {
        // Open a new card per call. Pending until its tool message arrives.
        for (const call of calls) {
          const callId = call.id ?? `${msg.id}-${call.name}-${rows.length}`;
          const card: ToolCard = {
            callId,
            name: call.name ?? "tool",
            args: call.args ?? {},
            result: null,
            status: "pending",
          };
          cardByCallId.set(callId, card);
          rows.push({ kind: "card", key: `c-${callId}`, card });
        }
      }
    } else if (msg.type === "tool") {
      // Match into the card by tool_call_id. If no card exists (shouldn't
      // happen), drop silently — the user doesn't care about orphans.
      const callId = msg.tool_call_id;
      if (callId && cardByCallId.has(callId)) {
        const card = cardByCallId.get(callId)!;
        card.result = messageText(msg.content);
        card.status = "done";
      }
    }
  }
  return rows;
}

export default function App() {
  const apiUrl =
    import.meta.env.VITE_LANGGRAPH_API_URL ?? "http://127.0.0.1:2024";
  const [threadId, setThreadId] = useState<string | undefined>(
    () => new URLSearchParams(window.location.search).get("thread") ?? undefined,
  );
  const sessionUrl = threadId
    ? `${window.location.origin}${window.location.pathname}?thread=${threadId}`
    : null;

  const stream = useStream<StreamState>({
    apiUrl,
    assistantId: "research",
    threadId,
    onThreadId: (id) => {
      setThreadId(id);
      const url = new URL(window.location.href);
      url.searchParams.set("thread", id);
      window.history.replaceState({}, "", url);
    },
  });

  const [input, setInput] = useState("");
  const rows = useMemo(() => buildRows(stream.messages as Message[]), [stream.messages]);
  const todos = Array.isArray(stream.values?.todos) ? stream.values.todos : [];

  const bilingual = rows.some((row) => row.kind === "prose" && row.type === "human" && row.body === task1Prompt);
  const label = (english: string, chinese: string) => bilingual ? `${chinese} / ${english}` : english;

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || stream.isLoading) return;
    setInput("");
    stream.submit({ messages: [{ type: "human", content: text }] });
  }

  return (
    <main>
      <h1>{label("Research Deep Agent", "深度研究助手")}</h1>
      <section className="thread-banner" aria-label={label("Session link", "会话链接")}>
        <div className="thread-banner__copy">
          <strong>{threadId ? label("Session link active", "会话链接已生效") : "Session link ready"}</strong>
          <span>
            {threadId
              ? label("Reopen this conversation later with the current URL.", "以后可用当前网址重新打开此会话。")
              : "After the first message, this page adds a thread URL so you can reopen the same conversation later."}
          </span>
        </div>
        {sessionUrl ? <code className="thread-banner__url">{sessionUrl}</code> : null}
      </section>
      <TodoList todos={todos} translate={bilingual ? task1Todo : undefined} />

      <section className="chat" aria-label={label("Research conversation", "研究会话")}>
        {rows.length === 0 && (
          <p className="hint">
            Try: <em>"Research what LangGraph 1.0 added vs 0.x. Cite sources."</em>
          </p>
        )}
        {rows.map((row) => {
          if (row.kind === "plan") return <ThinkingBlock key={row.key} body={row.body} />;
          if (row.kind === "card") {
            return <ToolCallCard key={row.key} card={row.card} translation={bilingual ? task1Tool(row.card) : undefined} />;
          }

          const translated = bilingual ? task1Prose(row.body) : undefined;
          return (
            <article key={row.key} className={`msg msg--${row.type}`}>
              <header className="msg__role">{label(row.type, row.type === "human" ? "提问" : "研究助手")}</header>
              {translated && (
                <div className="msg__body translation" lang="zh-CN">
                  <p className="translation__label">中文</p>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{translated}</ReactMarkdown>
                </div>
              )}
              <div className={`msg__body${translated ? " translation translation--original" : ""}`} lang={translated ? "en" : undefined}>
                {translated && <p className="translation__label">English</p>}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{row.body}</ReactMarkdown>
              </div>
            </article>
          );
        })}
        {stream.isLoading && (
          <div className="activity-card" aria-live="polite" aria-label={label("Research in progress", "研究进行中")}>
            <div className="activity-card__pulse" aria-hidden="true">
              <span />
              <span />
              <span />
            </div>
            <div className="activity-card__copy">
              <strong>{label("Research in progress", "研究进行中")}</strong>
              <span>{label("Waiting for sub-agent results and final synthesis.", "正在等待子 Agent 的结果和最终汇总。")}</span>
            </div>
          </div>
        )}
        {stream.error ? <p className="error">{String(stream.error)}</p> : null}
      </section>

      <form className="composer" onSubmit={onSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={label("Ask a research question…", "输入研究问题…")}
          disabled={stream.isLoading}
          autoFocus
        />
        <button type="submit" disabled={stream.isLoading || !input.trim()}>
          {label("Send", "发送")}
        </button>
      </form>
    </main>
  );
}
