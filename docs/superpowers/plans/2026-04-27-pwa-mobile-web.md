# PWA Mobile Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first XDownloader PWA/mobile web release that calls the public Render API, displays extracted video/GIF/image results, and gives users clear download/open actions.

**Architecture:** Keep the existing React/Vite frontend and FastAPI backend. The frontend owns mobile-first UX, API base URL configuration, and PWA metadata; the backend only needs CORS configuration for deployed frontend origins.

**Tech Stack:** React 19, Vite 6, TypeScript, Vitest, FastAPI, Pydantic.

---

### Task 1: Public API Configuration

**Files:**
- Modify: `frontend/src/api.ts`
- Modify: `frontend/src/api.test.ts`

- [ ] Write a failing test proving `extractMedia` posts to a configured API base URL.
- [ ] Run `npm.cmd test -- src/api.test.ts` and confirm the new test fails.
- [ ] Add `VITE_API_BASE_URL` support with a same-origin fallback.
- [ ] Run `npm.cmd test -- src/api.test.ts` and confirm it passes.

### Task 2: Mobile-First Result UI

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/MediaResult.tsx`
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/App.test.tsx`

- [ ] Write failing tests for Chinese copy, loading guidance, and download/open result actions.
- [ ] Run `npm.cmd test -- src/App.test.tsx` and confirm the new tests fail.
- [ ] Replace garbled text, add mobile-first empty/loading/error states, and expose both download and open links for each media item.
- [ ] Run `npm.cmd test -- src/App.test.tsx` and confirm it passes.

### Task 3: PWA Metadata

**Files:**
- Create: `frontend/public/manifest.webmanifest`
- Create: `frontend/public/icon.svg`
- Modify: `frontend/index.html`

- [ ] Write a failing test or static check proving the manifest is linked from `index.html`.
- [ ] Run the check and confirm it fails.
- [ ] Add manifest, theme metadata, mobile viewport settings, and SVG icon.
- [ ] Run the check and confirm it passes.

### Task 4: Backend CORS for PWA Deployments

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_api.py`

- [ ] Write a failing test proving configured frontend origins are allowed by CORS.
- [ ] Run `pytest backend/tests/test_api.py` and confirm it fails.
- [ ] Read allowed origins from `XDOWNLOADER_CORS_ORIGINS`, preserving localhost defaults.
- [ ] Run `pytest backend/tests/test_api.py` and confirm it passes.

### Task 5: Documentation and Full Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/render-deployment.md`
- Modify: `docs/local-development.md`

- [ ] Update docs with the public API URL, PWA first-release path, and Android APK second-release path.
- [ ] Run frontend tests and build.
- [ ] Run backend tests.
- [ ] Review `git diff` for accidental unrelated changes.
