import type { ReactNode } from 'react';
import { messages } from '../i18n/en';

export interface OccurrenceRowProps {
  title: string;
  assignee?: string;
  dueLabel?: string;
  recurrence?: boolean;
  completed?: boolean;
  onComplete?: () => void;
  children?: ReactNode;
}

function OccurrenceRow({
  title,
  assignee,
  dueLabel,
  recurrence = false,
  completed = false,
  onComplete,
  children
}: OccurrenceRowProps) {
  return (
    <article className="card occurrence-row" aria-label={`Occurrence ${title}`}>
      <div className="occurrence-row__content">
        <div className="occurrence-row__title-row">
          <h3>{title}</h3>
          {completed ? <span className="pill">Completed</span> : null}
        </div>
        {assignee ? <p className="meta">{messages.assignee}: {assignee}</p> : null}
        {dueLabel ? <p className="meta">{dueLabel}</p> : null}
        {recurrence ? <p className="meta">{messages.recurrence}</p> : null}
        {children}
      </div>
      <button
        type="button"
        className="primary-button"
        aria-label={`${messages.markComplete} ${title}`}
        onClick={onComplete}
      >
        {messages.markComplete}
      </button>
    </article>
  );
}

export default OccurrenceRow;
