# i18n Setup Instructions

## Installation

Run the following command to install the required i18n packages:

```bash
npm install i18next react-i18next i18next-browser-languagedetector
```

## What's Been Implemented

### ✅ Created Files:

1. **`src/i18n/config.ts`** - i18n configuration with Ukrainian as default
   language
2. **`src/i18n/locales/en.json`** - Complete English translations
3. **`src/i18n/locales/ua.json`** - Complete Ukrainian translations
4. **`src/components/common/LanguageSwitcher.tsx`** - Language switcher
   component

### ✅ Modified Files:

1. **`src/main.tsx`** - Added i18n config import
2. **`src/components/layout/AppLayout.tsx`** - Integrated translations and
   language switcher

## Features

- 🇺🇦 **Ukrainian (UA) is the default language**
- 🔄 **EN/UA language switcher** in the header
- 💾 **Language preference persists** in localStorage
- 🎯 **Complete translations** for all UI elements including:
  - Navigation (Dashboard, History, Progress, Logout)
  - Authentication (Login, Register forms)
  - Dashboard (metrics, profile settings)
  - Job postings (create, browse, list)
  - Sessions (history, detail, answer forms)
  - Feedback (scores, gaps, recommendations)
  - Common UI elements (buttons, labels, errors)

## Usage in Components

To use translations in any component:

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.metrics.completedInterviews')}</p>
    </div>
  );
}
```

### With interpolation:

```typescript
const { t } = useTranslation();
const maxLength = 20000;

<p>{t('sessions.answer.errorTooLong', { max: maxLength })}</p>;
```

## Next Steps

To fully translate the application, update existing components by:

1. Adding `const { t } = useTranslation();` to the component
2. Replacing hardcoded text with `{t('translation.key')}`

All translation keys are already defined in the JSON files!

## Example: Translating Login Form

```typescript
// Before
<h2>Sign in to your account</h2>
<label>Email address</label>
<button>{isLoading ? 'Signing in...' : 'Sign in'}</button>

// After
const { t } = useTranslation();

<h2>{t('auth.login.title')}</h2>
<label>{t('auth.login.email')}</label>
<button>{isLoading ? t('auth.login.submitting') : t('auth.login.submit')}</button>
```

## Translation Keys Structure

The translations are organized hierarchically:

- `app.*` - Application title
- `nav.*` - Navigation items
- `auth.*` - Authentication (login, register)
- `dashboard.*` - Dashboard page
- `jobs.*` - Job postings
- `sessions.*` - Interview sessions
- `feedback.*` - Feedback display
- `progress.*` - Progress tracking
- `common.*` - Common UI elements
- `errors.*` - Error messages
- `operation.*` - Operation status messages
- `language.*` - Language switcher
