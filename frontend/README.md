# Frontend: React + TypeScript + Vite

A modern frontend for the PlanTracker application, built with React, TypeScript, and Vite.

**Live Demo:** [http://158.160.23.164/](http://158.160.23.164/)

## Overview
- **Framework:** React + TypeScript
- **Build Tool:** Vite
- **Linting:** ESLint with TypeScript support

## Setup
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at [http://localhost:3000](http://localhost:3000).

## Configuration
### ESLint
For production applications, enable type-aware lint rules:
```js
export default tseslint.config({
  extends: [
    ...tseslint.configs.recommendedTypeChecked,
    ...tseslint.configs.strictTypeChecked,
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

### React-Specific Linting
Install and configure React-specific lint rules:
```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```
