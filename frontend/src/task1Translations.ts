import phrases from "./task1/phrases.json";
import reportEn from "./task1/report.en.md?raw";
import reportZh from "./task1/report.zh.md?raw";
import researchEn from "./task1/research.en.md?raw";
import researchZh from "./task1/research.zh.md?raw";
import type { ToolCard, ToolCardTranslation } from "./ToolCallCard";

export const task1Prompt = phrases.prompt.en;
export const task1ReportEn = reportEn.trim();

const todoLabels = new Map(Object.entries(phrases.todos));
const prose = new Map([
  [task1Prompt, phrases.prompt.zh],
  [normalizedText(task1ReportEn), reportZh.trim()],
]);
const toolResults = new Map([
  ...Object.entries(phrases.confirmations),
  [normalizedText(researchEn), researchZh.trim()],
]);

// The saved file repeats the report body without its opening summary.
// Only ignore end-of-line spacing when matching that tool argument.
function reportBody(markdown: string): string {
  return markdown.slice(markdown.indexOf("\n# ") + 1).trim();
}

function normalizedText(markdown: string): string {
  return markdown.replace(/(?:[ \t]+|\\)$/gm, "").trim();
}

const savedReportEn = normalizedText(reportBody(reportEn));
const savedReportZh = reportBody(reportZh);
const toolArguments = new Map([
  ...todoLabels,
  [task1Prompt, phrases.prompt.zh],
  [phrases.researchTask.en, phrases.researchTask.zh],
  ["pending", "待处理"],
  ["in_progress", "进行中"],
  ["completed", "已完成"],
]);

export function task1Prose(text: string): string | undefined {
  return prose.get(normalizedText(text));
}

export function task1Todo(text: string): string | undefined {
  return todoLabels.get(text);
}

function localizeArgument(value: unknown): unknown {
  if (typeof value === "string") {
    if (value.startsWith("# ") && normalizedText(value) === savedReportEn) return savedReportZh;
    return toolArguments.get(value) ?? value;
  }
  if (Array.isArray(value)) return value.map(localizeArgument);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, child]) => [key, localizeArgument(child)]),
    );
  }
  return value;
}

export function task1Tool(card: ToolCard): ToolCardTranslation {
  const translatedArgs = JSON.stringify(localizeArgument(card.args), null, 2);
  return {
    args: translatedArgs === JSON.stringify(card.args, null, 2) ? undefined : translatedArgs,
    result: card.result === null ? undefined : toolResults.get(normalizedText(card.result)),
  };
}
