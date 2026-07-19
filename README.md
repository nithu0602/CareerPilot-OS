# CareerPilot OS

AI-native career operating system for international students pursuing sponsored graduate roles.

CareerPilot helps users understand their current employability, find and rank suitable roles, tailor their application material, practise interviews, and follow a focused career plan.

## Start here

The build specification lives in [docs/PROJECT_BIBLE.md](docs/PROJECT_BIBLE.md). It is the single source of truth for scope, architecture, data contracts, agent behaviour, UX, and engineering standards.

## MVP modules

- Landing and authentication
- Career Health and resume intelligence
- Job discovery with explainable fit and sponsorship ranking
- Resume tailoring and cover letters
- Application tracking
- Interview coaching
- Four-week career strategy

## Repository layout

```text
frontend/     Next.js application
backend/      FastAPI application
docs/         product and engineering documentation
```

## Development sequence

1. Scaffold the frontend and backend according to the Project Bible.
2. Provision Supabase using the database schema in the Project Bible.
3. Implement APIs and UI in the stated feature order.
4. Use the acceptance criteria before considering any feature complete.

