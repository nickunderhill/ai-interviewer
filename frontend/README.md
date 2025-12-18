# AI Interviewer - Frontend

Frontend application for the AI Interviewer diploma project.

## Project Overview

This is the React-based frontend for an AI-powered technical interview practice system. The application helps users practice technical interviews with adaptive question generation and detailed feedback analysis.

## Technology Stack

- **React 18.3** - UI library with functional components and hooks
- **TypeScript 5.9** - Type-safe development with strict mode
- **Vite 7.x** - Fast build tool and dev server
- **Vitest** - Unit testing framework
- **React Testing Library** - Component testing utilities
- **ESLint** - Code quality and linting

## Getting Started

### Prerequisites

- Node.js 18+ (v22.14.0 recommended)
- pnpm package manager

### Installation

```bash
pnpm install
```

### Development

Start the dev server:

```bash
pnpm dev
```

The application will be available at http://localhost:5173

### Testing

Run tests:

```bash
pnpm test        # Run in watch mode
pnpm test:run    # Run once
pnpm test:ui     # Run with UI
```

### Build

Build for production:

```bash
pnpm build
```

### Linting

Run ESLint:

```bash
pnpm lint
```

## Project Structure

```
src/
├── App.tsx           # Main application component
├── main.tsx          # Application entry point
├── test/             # Test setup and utilities
└── assets/           # Static assets
```

## Architecture Alignment

- TypeScript strict mode enabled
- Functional components only (no class components)
- React 18.3 for stable production use
- Vite for fast development experience
- Port 5173 explicitly configured

## Future Dependencies

These will be added in subsequent stories:
- Tailwind CSS v3+
- TanStack Query v5
- React Router v6
- React Hook Form v7 with Zod
- Axios
