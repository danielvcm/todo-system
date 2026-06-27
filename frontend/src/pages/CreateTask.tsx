import { FormEvent, useMemo, useState } from 'react';
import { messages } from '../i18n/en';
import { request } from '../services/haConnector';

function CreateTask() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [assignee, setAssignee] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [recurrence, setRecurrence] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const isValid = useMemo(() => title.trim().length > 0 && (!startDate || !endDate || endDate >= startDate), [title, startDate, endDate]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!isValid) {
      setError(messages.invalidInterval);
      return;
    }

    setError(null);
    try {
      await request('create_task', {
        title,
        description,
        assignee_id: assignee ? Number(assignee) : undefined,
        start_due_date: startDate || undefined,
        end_due_date: endDate || undefined,
        recurrence_rule: recurrence ? { freq: recurrence } : undefined
      });
      setSuccess(true);
    } catch (err) {
      setSuccess(false);
      setError(err instanceof Error ? err.message : messages.error);
    }
  }

  return (
    <main className="page-shell">
      <section className="card" aria-labelledby="create-task-title">
        <h1 id="create-task-title">{messages.createTask}</h1>
        <form className="form-stack" onSubmit={handleSubmit}>
          <label className="input-group">
            <span>{messages.titleLabel}</span>
            <input value={title} onChange={(event) => setTitle(event.target.value)} required />
          </label>
          <label className="input-group">
            <span>{messages.descriptionLabel}</span>
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
          <label className="input-group">
            <span>{messages.assigneeLabel}</span>
            <input value={assignee} onChange={(event) => setAssignee(event.target.value)} placeholder="1" />
          </label>
          <div className="date-grid">
            <label className="input-group">
              <span>{messages.startDateLabel}</span>
              <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
            </label>
            <label className="input-group">
              <span>{messages.endDateLabel}</span>
              <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
            </label>
          </div>
          <label className="input-group">
            <span>{messages.recurrenceLabel}</span>
            <select value={recurrence} onChange={(event) => setRecurrence(event.target.value)}>
              <option value="">None</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </label>
          {error ? <p className="error">{error}</p> : null}
          {success ? <p className="success">Task saved.</p> : null}
          <button className="primary-button" type="submit" disabled={!isValid}>
            {messages.submit}
          </button>
        </form>
      </section>
    </main>
  );
}

export default CreateTask;
