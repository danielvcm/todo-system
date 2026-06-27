import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CreateTask from './CreateTask';
import * as haConnector from '../services/haConnector';

vi.mock('../services/haConnector', () => ({
  request: vi.fn()
}));

describe('CreateTask', () => {
  it('submits a task when the form is valid', async () => {
    const user = userEvent.setup();
    vi.mocked(haConnector.request).mockResolvedValue({ id: '1', status: 'ok' });

    render(<CreateTask />);

    await user.type(screen.getByLabelText(/title/i), 'Clean kitchen');
    await user.type(screen.getByLabelText(/description/i), 'Take out trash');
    await user.type(screen.getByLabelText(/assignee/i), '1');
    await user.type(screen.getByLabelText(/start date/i), '2026-06-27');
    await user.type(screen.getByLabelText(/end date/i), '2026-06-27');
    await user.selectOptions(screen.getByLabelText(/recurrence/i), 'weekly');

    await user.click(screen.getByRole('button', { name: /save task/i }));

    expect(haConnector.request).toHaveBeenCalled();
  });
});
