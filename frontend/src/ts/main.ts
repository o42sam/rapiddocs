import '../styles/main.css';
import { DocumentForm } from './components/DocumentForm';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  console.log('Document Generator initialized');

  // Initialize the main form
  try {
    new DocumentForm('document-form');
  } catch (error) {
    console.error('Failed to initialize application:', error);
  }
});
