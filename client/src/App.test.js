import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the generic RAG search heading', () => {
  render(<App />);
  expect(screen.getByText(/rag search/i)).toBeInTheDocument();
});
