# Document Generator Frontend

TypeScript + Tailwind CSS frontend for the Document Generator application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
```

3. Run development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Features

- Responsive design with Tailwind CSS
- TypeScript for type safety
- Dynamic form with statistics management
- Color theme selector
- File upload with validation
- Real-time generation progress
- PDF download

## Project Structure

```
src/
├── index.html           # Main HTML
├── ts/
│   ├── main.ts         # Entry point
│   ├── api/            # API client
│   ├── components/     # UI components
│   ├── types/          # TypeScript types
│   └── utils/          # Utilities
└── styles/
    └── main.css        # Tailwind + custom styles
```
