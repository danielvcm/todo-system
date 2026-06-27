import { useEffect, useState } from 'react';
import { messages } from '../i18n/en';
import { request } from '../services/haConnector';
import OccurrenceRow from './OccurrenceRow';

interface OccurrenceItem {
  occurrence_id?: number;
  task?: {
    id?: number;
    title?: string;
    assignee_id?: number;
  };
  date?: string;
  status?: string;
}

function DueList() {
  const [items, setItems] = useState<OccurrenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    request('list_due', { date: new Date().toISOString().slice(0, 10) })
      .then((response) => {
        if (!isMounted) {
          return;
        }
        const occurrences = ((response.data?.occurrences as OccurrenceItem[]) ?? []) as OccurrenceItem[];
        setItems(occurrences);
        setLoading(false);
      })
      .catch((err: Error) => {
        if (!isMounted) {
          return;
        }
        setError(err.message || messages.error);
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <p className="state-card">{messages.loading}</p>;
  }

  if (error) {
    return <p className="state-card error">{error}</p>;
  }

  if (!items.length) {
    return <p className="state-card">{messages.empty}</p>;
  }

  return (
    <div className="list-stack" role="list">
      {items.map((item) => (
        <OccurrenceRow
          key={item.occurrence_id ?? item.task?.id ?? item.date}
          title={item.task?.title ?? 'Untitled'}
          assignee={item.task?.assignee_id ? `#${item.task.assignee_id}` : undefined}
          dueLabel={item.date ? `Due ${item.date}` : undefined}
          recurrence={Boolean(item.occurrence_id && item.task?.id)}
          completed={item.status === 'completed'}
          onComplete={() => undefined}
        />
      ))}
    </div>
  );
}

export default DueList;
