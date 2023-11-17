import { render } from '@testing-library/react';
import { test } from '@jest/globals';
import App from 'App';

test('renders the landing page', () => {
	render(<App />);
});