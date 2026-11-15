import type { ReactNode } from "react";

export type TodoStatus = "pending" | "in_progress" | "completed";

export type TodoItem = {
  content: string;
  status: TodoStatus;
};

function statusLabel(status: TodoStatus): string {
  switch (status) {
    case "completed":
      return "done";
    case "in_progress":
      return "active";
    default:
      return "queued";
  }
}

const chineseStatus = { completed: "已完成", in_progress: "进行中", pending: "待处理" };

export default function TodoList({
  todos,
  translate,
}: { todos: TodoItem[]; translate?: (content: string) => string | undefined }): ReactNode {
  if (todos.length === 0) return null;

  const completedCount = todos.filter((todo) => todo.status === "completed").length;
  const progress = Math.round((completedCount / todos.length) * 100);

  const title = translate ? "研究计划 / Research plan" : "Research plan";

  return (
    <section className="todo-panel" aria-label={title}>
      <div className="todo-panel__header">
        <div>
          <p className="todo-panel__eyebrow">{translate ? "实时进度 / Live progress" : "Live progress"}</p>
          <h2 className="todo-panel__title">{title}</h2>
        </div>
        <div className="todo-panel__summary">
          <strong>{progress}%</strong>
          <span>{completedCount}/{todos.length} {translate ? "已完成 / completed" : "completed"}</span>
        </div>
      </div>

      <ol className="todo-list">
        {todos.map((todo, index) => {
          const chinese = translate?.(todo.content);
          const status = statusLabel(todo.status);
          return (
            <li key={`${todo.content}-${index}`} className={`todo-list__item todo-list__item--${todo.status}`}>
              <span className="todo-list__index">{index + 1}</span>
              <span className="todo-list__content">
                {chinese && <span className="todo-list__translation" lang="zh-CN">{chinese}</span>}
                <span lang={chinese ? "en" : undefined}>{todo.content}</span>
              </span>
              <span className={`todo-list__status todo-list__status--${todo.status}`}>
                {translate ? `${chineseStatus[todo.status]} / ${status}` : status}
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
