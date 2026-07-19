# CareerPilot OS
## Phase 1 — Foundation & Enterprise Project Setup

Read the attached project documents before writing any code.

Priority order:
1. Project Bible
2. Technical Design Document
3. Master Engineering Prompt
4. Engineering Revision Specification

These documents define the architecture and are the source of truth.

DO NOT build backend features.
DO NOT build AI.
DO NOT build database models.
DO NOT build authentication.

This phase is ONLY about creating a production-quality foundation.

-------------------------------------------------------
GOAL
-------------------------------------------------------

Build an enterprise-grade Next.js 15 codebase that will support the complete CareerPilot OS architecture.

The project must compile without warnings.

The project must look like a real startup repository.

Everything should be modular.

Everything should be reusable.

Strict TypeScript everywhere.

No placeholder "any" types.

No TODO comments.

No unfinished files.

-------------------------------------------------------
STACK
-------------------------------------------------------

Framework
- Next.js 15 App Router
- React 19
- TypeScript (strict)

Styling

- Tailwind CSS v4

UI

- shadcn/ui

Animation

- Framer Motion

Icons

- Lucide React

Validation

- Zod

State

- TanStack React Query

Forms

- React Hook Form

Utilities

- clsx
- class-variance-authority
- tailwind-merge

Testing

- Vitest
- Playwright

Quality

- ESLint
- Prettier
- Husky
- lint-staged

-------------------------------------------------------
PROJECT STRUCTURE
-------------------------------------------------------

Create the following structure.

app/

components/

components/ui

components/layout

components/common

features/

resume/

jobs/

dashboard/

strategy/

interview/

learning/

applications/

settings/

agents/

coordinator/

db/

hooks/

lib/

services/

types/

schemas/

utils/

constants/

styles/

public/

-------------------------------------------------------
ROUTES
-------------------------------------------------------

Create placeholder pages.

/

login

register

dashboard

resume

jobs

applications

interview

strategy

learning

settings

Each page should use the AppShell layout.

Each page should have:

title

description

placeholder content

No business logic.

-------------------------------------------------------
LAYOUT
-------------------------------------------------------

Create:

AppShell

Sidebar

TopBar

Navigation

Breadcrumbs

Responsive layout

Dark mode support

Theme Provider

Sidebar collapse

Mobile drawer

-------------------------------------------------------
GLOBAL DESIGN SYSTEM
-------------------------------------------------------

Create reusable components.

Button

Input

Textarea

Select

Card

MetricCard

SectionHeader

PageHeader

Badge

Avatar

Dialog

Drawer

Tabs

Table

Skeleton

Spinner

Progress

ScoreRing

StatusBadge

EmptyState

ErrorState

LoadingState

ActionCard

ReasonList

Everything should be reusable.

-------------------------------------------------------
THEME
-------------------------------------------------------

Configure:

Dark mode

Typography

Spacing

Color tokens

Radius

Container sizes

Animation presets

-------------------------------------------------------
UTILITY FUNCTIONS
-------------------------------------------------------

Create:

cn()

formatDate()

formatPercentage()

formatScore()

sleep()

safeParseJSON()

downloadFile()

debounce()

throttle()

logger()

-------------------------------------------------------
LOGGER
-------------------------------------------------------

Build a structured logger.

logger.info()

logger.warn()

logger.error()

logger.debug()

Environment-aware.

Pretty in development.

Minimal in production.

-------------------------------------------------------
GLOBAL TYPES
-------------------------------------------------------

Create shared types.

User

Resume

Job

Application

Agent

ESPScore

Recommendation

Interview

LearningPlan

APIResponse

APIError

PaginatedResponse

Status

ID

Timestamp

-------------------------------------------------------
SHARED ZOD SCHEMAS
-------------------------------------------------------

Create schemas for:

User

Resume

Job

Application

ESP

Recommendation

Interview

LearningPlan

Environment

Export everything.

-------------------------------------------------------
ENVIRONMENT
-------------------------------------------------------

Create environment validation.

Use Zod.

Validate:

NEXT_PUBLIC_SUPABASE_URL

NEXT_PUBLIC_SUPABASE_ANON_KEY

SUPABASE_SERVICE_ROLE_KEY

OPENAI_API_KEY

NODE_ENV

Fail immediately if invalid.

-------------------------------------------------------
CONFIGURATION
-------------------------------------------------------

Create:

site.ts

navigation.ts

theme.ts

constants.ts

routes.ts

env.ts

-------------------------------------------------------
ERROR HANDLING
-------------------------------------------------------

Global Error Boundary

404 page

Loading page

Global error page

-------------------------------------------------------
CODE QUALITY
-------------------------------------------------------

Enable:

Strict TypeScript

Absolute imports

Path aliases

ESLint

Prettier

Husky

lint-staged

EditorConfig

Git ignore

-------------------------------------------------------
REACT QUERY
-------------------------------------------------------

Create QueryClientProvider.

No API calls.

Only infrastructure.

-------------------------------------------------------
ANIMATIONS
-------------------------------------------------------

Create reusable motion presets.

Fade

Slide

Scale

Page transition

-------------------------------------------------------
ACCESSIBILITY
-------------------------------------------------------

Keyboard navigation

ARIA labels

Semantic HTML

Focus management

-------------------------------------------------------
TESTING
-------------------------------------------------------

Configure:

Vitest

Playwright

Testing utilities

One sample test.

-------------------------------------------------------
DO NOT BUILD
-------------------------------------------------------

No database

No Drizzle

No Supabase

No AI

No OpenAI

No API routes

No authentication

No Coordinator

No Agents

No business logic

No resume upload

No ESP calculations

-------------------------------------------------------
EXPECTED OUTPUT
-------------------------------------------------------

When complete provide:

1. Folder tree

2. Packages installed

3. Files created

4. Architecture decisions

5. Lint status

6. TypeScript status

7. Build status

8. Test status

9. Remaining work for Phase 2

Do not proceed to Phase 2.

Stop after the foundation is complete.