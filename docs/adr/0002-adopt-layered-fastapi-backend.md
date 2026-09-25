# 0002 Adopt Layered FastAPI Backend

## Status

Accepted

## Context

The backend needs a predictable structure that separates HTTP transport, validation, business logic, persistence access, and persistence models.

Without explicit layering, FastAPI route handlers can easily accumulate business rules, data access, and transport behavior in one place.

## Decision

The backend will follow a layered structure built around:

- routes
- schemas
- services
- repositories
- models

Responsibilities are separated as follows:

- routes handle HTTP entry and response mapping
- schemas validate and serialize contracts
- services enforce business workflows and rules
- repositories isolate database access
- models represent persistence structures

## Consequences

Benefits:

- clearer ownership boundaries
- better testability per layer
- easier review of business logic vs. persistence logic
- stronger compatibility with shared contract and security rules

Costs and tradeoffs:

- more modules than a minimal inline FastAPI structure
- contributors must preserve discipline to keep routes thin

## Alternatives Considered

### Fat Route Handlers

Rejected because they mix transport, business, and persistence concerns and become harder to test and review.

### Service-Less CRUD Structure

Rejected because it does not scale well once authorization, orchestration, and domain rules become more complex.
