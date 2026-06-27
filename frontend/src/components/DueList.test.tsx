import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import DueList from './DueList';
import * as haConnector from '../services/haConnector';

vi.mock('../services/haConnector', () => ({
  request: vi.fn()
}));

describe('DueList', () => {
  it('renders an empty state when no chores are due', async () => {
    vi.mocked(haConnector.request).mockResolvedValue({ id: '1', status: 'ok', data: { occurrences: [] } });

    render(<DueList />);

    await waitFor(() => expect(screen.getByText(/nothing due today/i)).toBeInTheDocument());
  });
});
