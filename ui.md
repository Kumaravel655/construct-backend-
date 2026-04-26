# Mobile App Retrofit Plan

## 1. Goal
Retrofit the existing Expo React Native app in `MyConstructorApp-main` so it matches the current backend APIs and the new data model, instead of continuing with the old flat-role and single-attendance assumptions.

The app already exists, so this is not a greenfield build. The work is to:

1. Replace stale role logic with the new `account_type` + `grade` model.
2. Replace old attendance flows with session-based geo attendance.
3. Add daily worklist workflows.
4. Add admin attendance analytics and movement views.
5. Add fund management screens for the `/api/funds/` module.
6. Keep the existing project, task, document, vendor, equipment, safety, communication, and finance screens working against the current backend routes.

## 2. Existing Mobile App Audit

### Current app structure

The app folder already contains a full Expo app with:

1. `App.js` boot screen and navigator hookup.
2. `navigation/AppNavigator.js` with role dashboards and module screens.
3. `screens/LoginScreen.js` and `screens/SignupScreen.js`.
4. Dashboards for admin, project manager, engineer, foreman, subcontractor, worker, safety officer, and quality inspector.
5. Shared module screens for projects, tasks, documents, budget, purchase orders, vendors, reports, users, equipment, safety, communications, attendance, invoices, and material requests.
6. `utils/api.js` with Axios wrappers and AsyncStorage token storage.
7. `utils/rolePermissions.js` with the old role names.

### What is already usable

1. The app already has navigation, authentication forms, and dashboard layouts.
2. Location and map libraries are already installed.
3. Document picker support already exists.
4. The app has enough screens to evolve into a production field app without rebuilding from zero.

### What is stale or mismatched

1. Authentication and role mapping still use the old `role` field instead of `account_type` and `grade`.
2. `attendanceAPI` still talks to the old single-record attendance shape.
3. Check-in and check-out logic is based on one attendance row per day, not session-based movement.
4. `SignupScreen` still posts old role values like `project_manager`, `site_engineer`, and `worker`.
5. Dashboard access control still keys off the old role names.
6. Several screens simulate data locally or assume old field names, so they need API alignment.
7. Some backend modules now exist under new app roots like `/api/gov/`, `/api/funds/`, `/api/investors/`, `/api/transport/`, `/api/qs/`, `/api/drawings/`, `/api/estimation/`, `/api/meetings/`, and `/api/reports/`.

## 3. Gap Analysis

### A. Authentication and user model gap

Current app:

1. Uses old flat roles in `utils/rolePermissions.js`.
2. Saves only `access`, `refresh`, and a raw `user` object.
3. Routes based on old role keys.

Backend now expects:

1. `account_type` values: `md`, `admin`, `technical`, `transport`.
2. `grade` values like `md_head`, `admin_head`, `admin_a1`, `admin_a2`, `tech_head`, `tech_se`, `tech_qs`, `tech_cd`, `tech_ee`, `tech_so`, `tech_qi`, `tech_fm`, `tech_sc`, `tech_wk`, `tr_head`, `tr_do`.
3. JWT login response with user profile fields that include `account_type`, `grade`, and display labels.

### B. Attendance gap

Current app:

1. Uses single attendance record per day.
2. Assumes `check_in_time`, `check_out_time`, `latitude`, and `longitude` on one row.
3. Does not support multiple site/office/travel/lunch sessions in the same day.
4. Does not show route points or distance trend.

Backend now provides:

1. `attendance-sessions/check-in/`
2. `attendance-sessions/{id}/check-out/`
3. `attendance-sessions/my-open-session/`
4. `attendance-sessions/my-day-sessions/`
5. `attendance-sessions/my-day-summary/`
6. `attendance-sessions/admin-user-day-route/`
7. `attendance-sessions/admin-day-overview/`
8. `attendance-sessions/admin-user-distance-trend/`

### C. Daily worklist gap

Current app:

1. Has task screens, but they are not a daily user worklist.
2. Tasks are often treated as project tasks or dashboard cards.
3. There is no daily personal worklist lifecycle with start, block, complete, and reopen.

Backend now provides:

1. `daily-work-items/`
2. `daily-work-items/my-day/`
3. `daily-work-items/{id}/start/`
4. `daily-work-items/{id}/complete/`
5. `daily-work-items/{id}/block/`
6. `daily-work-items/{id}/reopen/`
7. `daily-work-items/admin-team-worklist/`

### D. Fund management gap

Current app:

1. Has budget and invoice screens, but no dedicated fund management flow.
2. Does not expose fund sources, allotments, releases, and transaction ledger UI.

Backend now provides:

1. `/api/funds/fund-sources/`
2. `/api/funds/fund-allotments/`
3. `/api/funds/fund-allotments/{id}/release/`
4. `/api/funds/fund-transactions/`
5. `/api/funds/fund-summary/`

### E. Module coverage gap

The mobile app has screens for many backend entities, but some screens need endpoint remapping:

1. Documents should continue to use the document API but should be aligned with current upload behavior.
2. Project management must stay synced with project coordinates, budgets, and progress data.
3. Reports and analytics should be split into the new report flows and analytics flows.
4. Attendance tracking should be split into session-based attendance and admin analytics.

## 4. Target Mobile Architecture

### 4.1 App shell

1. Keep Expo React Native as the base.
2. Keep the current navigation stack, but replace the route decision logic.
3. Add a proper app bootstrap that loads auth state before showing screens.

### 4.2 State strategy

Recommended state layers:

1. `auth store` for token and user profile.
2. `server state` for API data, cached with query keys by module and filter.
3. `ui state` for drawers, modals, selected dates, and map state.

### 4.3 API layer strategy

1. Keep Axios as the request layer.
2. Replace hardcoded role assumptions with token-driven header injection.
3. Add API modules for attendance sessions, worklist, funds, admin analytics, and current existing modules.
4. Normalize backend responses into screen-friendly view models.

### 4.4 Role routing strategy

Route after login by `grade`, not old role names.

Suggested mapping:

1. `md_head` -> MD dashboard.
2. `admin_head`, `admin_a1`, `admin_a2` -> office/admin dashboards.
3. `tech_head` -> project manager dashboard.
4. `tech_se`, `tech_so`, `tech_qi`, `tech_fm`, `tech_wk`, `tech_sc`, `tech_qs`, `tech_cd`, `tech_ee` -> technical work dashboards.
5. `tr_head`, `tr_do` -> transport dashboard.

## 5. Screen Map by Role

### 5.1 Common screens

1. Login.
2. Signup or user onboarding.
3. Profile.
4. Notifications or messages.
5. Settings.

### 5.2 Worker and field user screens

1. Home.
2. Attendance Sessions.
3. Day Summary.
4. Daily Worklist.
5. My Tasks or assigned tasks.
6. Communication / instructions.

### 5.3 Project manager and technical lead screens

1. Project overview.
2. Team overview.
3. Task assignment.
4. Daily reports.
5. Attendance overview.
6. Documents.
7. Materials and procurement.

### 5.4 Admin and office screens

1. User management.
2. Attendance analytics.
3. Route and movement map.
4. Worklist monitoring.
5. Budget and invoices.
6. Fund management.
7. Reports and approvals.

### 5.5 Transport screens

1. Vehicle list.
2. Trip sheets.
3. Fuel logs.
4. Maintenance alerts.

## 6. Mobile Retrofit Plan by Module

## 6.1 Authentication module

### Current files to change

1. `MyConstructorApp-main/screens/LoginScreen.js`
2. `MyConstructorApp-main/screens/SignupScreen.js`
3. `MyConstructorApp-main/utils/rolePermissions.js`
4. `MyConstructorApp-main/utils/api.js`
5. `MyConstructorApp-main/navigation/AppNavigator.js`

### Implementation plan

1. Update login to store the new profile shape returned by backend.
2. Replace old role checks with `account_type` and `grade` checks.
3. Create a central auth context or store.
4. Replace signup role selector with account type and grade selector.
5. Add logout and token-clearing flow.

### API mapping

1. `POST /api/auth/login/`
2. `POST /api/auth/signup/`
3. `GET /api/auth/users/me/` if added later, or reuse login response profile.

## 6.2 Attendance module

### Existing gap

The current attendance screen still assumes one check-in and one check-out per day.

### New screens needed

1. Attendance Home.
2. Check In modal or drawer.
3. Check Out modal or drawer.
4. My Day Summary.
5. Session timeline.
6. Admin route map view.
7. Admin day overview table.
8. Distance trend chart.

### UX rules

1. First check-in of the day must show project, location type, and travel km.
2. Each session should show sequence number, timestamps, and geo coordinates.
3. Check out should only be available if there is an open session.
4. Movement analytics must show route points in order.
5. Empty states must be explicit, not blank.

### API mapping

1. `POST /api/auth/attendance-sessions/check-in/`
2. `PATCH /api/auth/attendance-sessions/{id}/check-out/`
3. `GET /api/auth/attendance-sessions/my-open-session/`
4. `GET /api/auth/attendance-sessions/my-day-sessions/?date=YYYY-MM-DD`
5. `GET /api/auth/attendance-sessions/my-day-summary/?date=YYYY-MM-DD`
6. `GET /api/auth/attendance-sessions/admin-user-day-route/?user={id}&date=YYYY-MM-DD`
7. `GET /api/auth/attendance-sessions/admin-day-overview/?date=YYYY-MM-DD`
8. `GET /api/auth/attendance-sessions/admin-user-distance-trend/?user={id}&start=YYYY-MM-DD&end=YYYY-MM-DD`

## 6.3 Daily worklist module

### Existing gap

The current task screens are project-task oriented, not a daily personal worklist.

### New screens needed

1. My Day Worklist.
2. Work Item Create/Edit.
3. Work Item Details.
4. Team Worklist Board for admin.

### UX rules

1. A user should be able to add a daily item in one quick form.
2. Start, complete, and block actions should be one-tap actions.
3. Blocked items must require a blocker note.
4. Completed items should show immutable status by default.

### API mapping

1. `GET /api/auth/daily-work-items/my-day/?date=YYYY-MM-DD`
2. `POST /api/auth/daily-work-items/`
3. `PATCH /api/auth/daily-work-items/{id}/start/`
4. `PATCH /api/auth/daily-work-items/{id}/complete/`
5. `PATCH /api/auth/daily-work-items/{id}/block/`
6. `PATCH /api/auth/daily-work-items/{id}/reopen/`
7. `GET /api/auth/daily-work-items/admin-team-worklist/`

## 6.4 Project management module

### Current state

Project management already exists in the app, but it needs cleanup for the current backend payloads and navigation consistency.

### Implementation plan

1. Keep the current project list and create/edit forms.
2. Ensure project manager selection, coordinates, and date fields match backend.
3. Reuse project progress percentage from the API.
4. Add better empty and loading states.

### API mapping

1. `GET /api/auth/projects/`
2. `POST /api/auth/projects/`
3. `PATCH /api/auth/projects/{id}/`
4. `GET /api/auth/projects/export-excel/`

## 6.5 Task and report module

### Implementation plan

1. Keep task assignment screens.
2. Update task status labels to reflect the backend `work_status` field.
3. Keep report screens but map them to the new backend report model where needed.
4. Show a clean separation between project tasks and daily work items.

### API mapping

1. `GET /api/auth/tasks/`
2. `POST /api/auth/tasks/`
3. `PATCH /api/auth/tasks/{id}/`
4. `GET /api/reports/daily-reports/`
5. `POST /api/reports/daily-reports/{id}/submit/`
6. `POST /api/reports/daily-reports/{id}/pm-review/`
7. `POST /api/reports/daily-reports/{id}/om-consolidate/`
8. `POST /api/reports/daily-reports/{id}/md-review/`

## 6.6 Documents module

### Implementation plan

1. Keep document picker support.
2. Ensure upload uses multipart form data.
3. Keep project and document type filters.
4. Add upload progress and failure retry.

### API mapping

1. `GET /api/auth/documents/`
2. `POST /api/auth/documents/`
3. `PATCH /api/auth/documents/{id}/`
4. `DELETE /api/auth/documents/{id}/`

## 6.7 Budget, invoice, vendor, purchase order, equipment, safety, and communication modules

### Implementation plan

1. Keep these screens but update data assumptions to current backend field names.
2. Replace any local dummy data with API data and robust empty states.
3. Keep filters by project, status, and date where applicable.
4. Make sure list cards display the computed fields now returned by the backend.

### API mapping

1. `/api/auth/budgets/`
2. `/api/auth/invoices/`
3. `/api/auth/vendors/`
4. `/api/auth/purchaseorders/`
5. `/api/auth/equipment/`
6. `/api/auth/incidents/`
7. `/api/auth/communications/`
8. `/api/auth/material-requests/`
9. `/api/auth/quality-inspections/`

## 6.8 Fund management module

### New screens needed

1. Fund Summary.
2. Fund Sources.
3. Fund Allotments.
4. Fund Release modal.
5. Fund Transactions.

### UX rules

1. Fund release must validate pending balance before allowing submit.
2. Allotment cards must show allotted, released, and pending values.
3. Finance users need quick access to source and release actions.

### API mapping

1. `GET /api/funds/fund-summary/`
2. `GET /api/funds/fund-sources/`
3. `POST /api/funds/fund-sources/`
4. `PATCH /api/funds/fund-sources/{id}/`
5. `GET /api/funds/fund-allotments/`
6. `POST /api/funds/fund-allotments/`
7. `PATCH /api/funds/fund-allotments/{id}/`
8. `POST /api/funds/fund-allotments/{id}/release/`
9. `GET /api/funds/fund-transactions/`

## 6.9 Transport module

### New screens needed

1. Vehicle list.
2. Vehicle detail.
3. Trip sheet list.
4. Trip sheet create and complete.
5. Fuel logs.
6. Maintenance alerts.

### API mapping

1. `/api/transport/vehicles/`
2. `/api/transport/trip-sheets/`
3. `/api/transport/fuel-logs/`
4. `/api/transport/fuel-summary/`

## 7. Data and State Model

### Auth state

Store:

1. access token.
2. refresh token.
3. serialized user profile.
4. `account_type`.
5. `grade`.
6. a computed dashboard route.

### Server state

Keep these as API-backed collections:

1. projects.
2. tasks.
3. documents.
4. attendance sessions.
5. daily work items.
6. fund sources and allotments.
7. fund transactions.
8. admin analytics data.

### UI state

Use local state only for:

1. open/close drawers and modals.
2. selected date.
3. map coordinate preview.
4. temporary form data.

## 8. Design Direction

The current mobile app has a blue corporate look. Keep the brand, but make it more polished and more field-friendly.

### Visual style

1. Industrial and practical.
2. High contrast.
3. Clear card hierarchy.
4. Simple status chips.
5. Strong empty states.

### Typography

1. Bold headers.
2. Large numeric KPI text.
3. Smaller helper text for timestamps and location metadata.

### Core UI components to build

1. App shell and role-aware side menu.
2. KPI cards.
3. Session timeline cards.
4. Work item cards.
5. Map preview panel.
6. Release modal.
7. Table and filter row component.
8. Error and empty state component.

## 9. Implementation Phases

### Phase 1: Retrofit auth and routing

1. Update login/signup payloads.
2. Replace old role model handling.
3. Add auth bootstrap and persistent user profile loading.
4. Update navigator to route by `grade`.

### Phase 2: Attendance sessions

1. Build session check-in and check-out UI.
2. Build day summary and timeline UI.
3. Add map preview and location capture.
4. Support admin route and overview screens.

### Phase 3: Daily worklist

1. Add personal worklist screens.
2. Add start, complete, block, reopen flows.
3. Add admin worklist board.

### Phase 4: Module cleanup

1. Align project, task, document, budget, PO, vendor, equipment, safety, and communication screens to current API fields.
2. Replace any local fallback data that should now come from the backend.

### Phase 5: Fund and transport modules

1. Add fund management screens.
2. Add transport screens.
3. Wire APIs and filters.

### Phase 6: Polish and hardening

1. Better loading skeletons.
2. Better empty states.
3. Offline or error fallbacks.
4. Permissions cleanup.
5. Platform-specific testing.

## 10. API Integration Checklist

### Must fix in `utils/api.js`

1. Replace hardcoded role assumptions.
2. Add attendance sessions endpoints.
3. Add daily worklist endpoints.
4. Add fund endpoints.
5. Ensure multipart document upload works on mobile.
6. Add response normalization helpers.

### Must fix in `utils/rolePermissions.js`

1. Convert old role keys into grade-based mapping.
2. Compute dashboard route from `grade`.
3. Keep helper permissions for screen gating.

### Must fix in `AppNavigator.js`

1. Add role bootstrap before route rendering.
2. Hide outdated routes that no longer apply.
3. Keep shared module screens but map them from the correct dashboards.

## 11. Suggested Deliverables

1. Updated Expo app shell with auth bootstrap.
2. New role and grade routing.
3. Attendance session UI.
4. Daily worklist UI.
5. Admin analytics UI.
6. Fund management UI.
7. Transport UI.
8. Clean API service layer.
9. Documented screen-to-endpoint map.

## 12. Recommended Build Order

1. Auth and route migration.
2. Attendance sessions.
3. Daily worklist.
4. Admin analytics.
5. Fund management.
6. Transport.
7. Existing screen cleanup.
8. Final polish and QA.

## 13. Acceptance Criteria

1. A user can log in and land on the correct dashboard based on `grade`.
2. A worker can create multiple attendance sessions in one day with geo coordinates.
3. A worker can submit, start, block, and complete daily work items.
4. Admin can view day overview, route points, and distance trends.
5. Finance can view fund summaries and release allotments with validation.
6. Existing project, task, document, and procurement screens still work after the retrofit.

## 14. Acceptance Criteria

1. Worker can check in and check out with required validation in under 20 seconds on mobile.
2. Worker can submit and update daily work items with state transitions.
3. Admin can view user-day route and distance trend without manual refresh glitches.
4. Finance user can release funds with strict pending amount validation.
5. Every primary page has clear loading, empty, and error states.
