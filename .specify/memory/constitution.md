# SI Extraction Using SpecKit Constitution

## Core Principles

### I. Code Quality (Non-Negotiable)
All code MUST adhere to the following standards:
- Single Responsibility Principle: Each module, class, or function has one clear purpose
- DRY (Don't Repeat Yourself): Code duplication is eliminated through abstraction and reuse
- Meaningful naming: Variables, functions, and classes use descriptive names that convey intent
- Maintainability first: Code is written for human readers first, machines second
- Static analysis required: All code passes linting, formatting, and type checking before PR approval
- Code review mandatory: Minimum two approvals required; focus on logic, maintainability, and adherence to principles
- Cyclomatic complexity limits: Functions MUST not exceed complexity threshold (default: 10); complex logic refactored into smaller units
- Technical debt tracking: Issues created for deferred refactoring; debt cannot exceed 5% of feature work

### II. Testing Standards (Non-Negotiable)
Test-driven development is mandatory and enforced:
- TDD workflow: Tests written first → Requirements approved → Tests fail → Implementation → Tests pass → Refactor
- Unit test coverage minimum: 80% for all new code; 90% for critical paths
- Integration tests required: All service boundaries, data flows, and external API calls tested
- End-to-end testing: Critical user journeys must pass E2E tests before release
- Test maintenance: Tests are treated as first-class code; refactored and maintained alongside implementation
- Mock and fixture standards: Clear contracts for mocks; fixtures immutable and version-controlled
- Performance testing: Benchmarks established for critical operations; regressions detected automatically
- Accessibility testing: UI changes include WCAG compliance validation; AT (assistive technology) tested

### III. User Experience Consistency
All user-facing features MUST provide coherent, predictable interactions:
- Design system adherence: All UI components follow established design tokens, spacing, typography, and color palette
- Interaction patterns: Navigation, form submission, error handling, and confirmation follow consistent patterns
- Accessibility first: WCAG 2.1 AA compliance mandatory; keyboard navigation, screen readers, color contrast verified
- Error messaging: Clear, actionable feedback; avoid technical jargon; guide users toward resolution
- Loading states: Visual indicators for all asynchronous operations; timeouts handled gracefully
- Responsive design: Works on mobile (320px+), tablet, and desktop without layout breaks
- Internationalization ready: Text extracted to localization files; dates, numbers, currency respect locale
- User research validation: Mockups/prototypes validated with users before implementation; feedback incorporated

### IV. Performance Requirements
All features MUST meet strict performance standards:
- Page load target: First Contentful Paint (FCP) < 1.5s; Largest Contentful Paint (LCP) < 2.5s
- Core Web Vitals: Cumulative Layout Shift (CLS) < 0.1; Interaction to Next Paint (INP) < 200ms
- API response time: 95th percentile response time < 500ms for all endpoints; timeouts enforced at 30s
- Bundle size limits: Initial JS bundle < 200KB gzipped; lazy-load all non-critical code
- Database query performance: All queries execute in < 100ms (p95); N+1 queries eliminated; indexes validated
- Memory efficiency: No memory leaks; monitoring on production detects growth > 10MB/hour
- Caching strategy: HTTP caching headers set correctly; service worker cache invalidation automated
- Performance regression testing: Automated performance benchmarks in CI/CD; regressions > 5% fail pipeline

## Development Standards & Quality Gates

All features MUST pass the following gates before merge:
- Automated tests passing (unit + integration + E2E)
- Code coverage above thresholds
- Linting and formatting compliant
- Type checking with zero errors
- Performance benchmarks met
- Accessibility audit passing
- Code review approved by two peers
- Documentation complete and reviewed

## Governance

The constitution supersedes all other practices and guidance documents. Amendments require:
1. Documented rationale for change (issue link or discussion)
2. Affected principles clearly identified
3. Migration plan for existing work
4. Explicit approval before ratification

All pull requests MUST verify compliance with applicable principles. Complexity MUST be justified in PR description. This document is the source of truth for project standards and practices.

**Version**: 1.0.0 | **Ratified**: 2026-05-04 | **Last Amended**: 2026-05-04
