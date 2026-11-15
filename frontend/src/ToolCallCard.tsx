import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Status = "pending" | "done";

export type ToolCard = {
  callId: string;
  name: string;
  args: unknown;
  result: string | null;
  status: Status;
};

export type ToolCardTranslation = { args?: string; result?: string };

function formatArgs(args: unknown): string {
  try {
    return JSON.stringify(args, null, 2);
  } catch {
    return String(args);
  }
}

export default function ToolCallCard({
  card,
  translation,
}: { card: ToolCard; translation?: ToolCardTranslation }): ReactNode {
  const [open, setOpen] = useState(card.status === "pending");
  const previousStatus = useRef<Status>(card.status);

  useEffect(() => {
    if (previousStatus.current === "pending" && card.status === "done") {
      setOpen(false);
    }
    previousStatus.current = card.status;
  }, [card.status]);

  const label =
    card.name === "task"
      ? "Sub-agent: research-agent"
      : `Tool: ${card.name}`;
  const badge = card.status === "pending" ? "running…" : "done";
  const chineseLabel = card.name === "task" ? "子 Agent" : "工具";
  const chineseBadge = card.status === "pending" ? "运行中" : "已完成";

  return (
    <details
      className={`tool-card tool-card--${card.status}`}
      open={open}
      onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}
    >
      <summary className="tool-card__summary">
        <span className="tool-card__name">{translation ? `${chineseLabel} / ${label}` : label}</span>
        <span className={`tool-card__badge tool-card__badge--${card.status}`}>{translation ? `${chineseBadge} / ${badge}` : badge}</span>
      </summary>
      <div className="tool-card__body">
        <div className="tool-card__section">
          <div className="tool-card__label">{translation ? "参数 / Arguments" : "arguments"}</div>
          {translation?.args && (
            <div lang="zh-CN">
              <p className="translation__label">中文</p>
              <pre className="tool-card__code">{translation.args}</pre>
            </div>
          )}
          <div lang={translation?.args ? "en" : undefined}>
            {translation?.args && <p className="translation__label">English</p>}
            <pre className="tool-card__code">{formatArgs(card.args)}</pre>
          </div>
        </div>
        {card.result !== null && (
          <div className="tool-card__section">
            <div className="tool-card__label">{translation ? "结果 / Result" : "result"}</div>
            {translation?.result && (
              <div lang="zh-CN">
                <p className="translation__label">中文</p>
                {card.name === "task" ? (
                  <div className="msg__body translation">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{translation.result}</ReactMarkdown>
                  </div>
                ) : (
                  <pre className="tool-card__code tool-card__code--result">{translation.result}</pre>
                )}
              </div>
            )}
            <div lang={translation?.result ? "en" : undefined}>
              {translation?.result && <p className="translation__label">English</p>}
              <pre className="tool-card__code tool-card__code--result">{card.result}</pre>
            </div>
          </div>
        )}
      </div>
    </details>
  );
}
