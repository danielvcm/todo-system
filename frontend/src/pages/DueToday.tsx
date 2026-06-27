import { Link } from 'react-router-dom';
import DueList from '../components/DueList';
import { messages } from '../i18n/en';

function DueToday() {
  return (
    <main className="page-shell">
      <section className="card page-header" aria-labelledby="due-today-title">
        <div>
          <p className="eyebrow">Home Assistant</p>
          <h1 id="due-today-title">{messages.dueTodayTitle}</h1>
        </div>
        <div className="page-header__actions">
          <label className="input-group" htmlFor="date-picker">
            <span>{messages.dueDateLabel}</span>
            <input id="date-picker" type="date" defaultValue={new Date().toISOString().slice(0, 10)} />
          </label>
          <Link className="primary-button" to="/create">
            {messages.createTask}
          </Link>
        </div>
      </section>
      <DueList />
    </main>
  );
}

export default DueToday;
