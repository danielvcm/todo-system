import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OccurrenceRow from './OccurrenceRow';

describe('OccurrenceRow', () => {
  it('renders the title, metadata, and accessible action', async () => {
    const user = userEvent.setup();
    const onComplete = vi.fn();

    render(
      <OccurrenceRow
        title="Vacuum living room"
        assignee="Alice"
        dueLabel="Due 2026-06-27"
        recurrence
        onComplete={onComplete}
      />
    );

    expect(screen.getByText('Vacuum living room')).toBeInTheDocument();
    expect(screen.getByText(/Assignee: Alice/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /mark complete vacuum living room/i })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /mark complete vacuum living room/i }));
    expect(onComplete).toHaveBeenCalledTimes(1);
  });
});
