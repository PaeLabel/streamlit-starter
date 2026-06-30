# STREAMLIT.md

> A spec for the LLM to read before generating this Streamlit app.
> Replace every `<placeholder>` and remove this quote block when done.
> Capture *intent* over implementation details. Let the agent pick the names.

## Purpose

<One or two sentences: what the app does and why it exists.>

- Primary user: <who uses this and what role they have>
- Job to be done: <what they accomplish with the app>
- Success looks like: <observable outcome that means it works>

## Personas

- <persona name>: <goals, frequency of use, technical level>
- <persona name>: <goals, frequency of use, technical level>

## Pages

> List each page with its layout intent, key inputs, and what state must persist.
> Use plain language. Do not name variables here.

- <Page name>: <layout summary>
  - Inputs: <widgets the user interacts with>
  - Persists: <what must survive a rerun or page switch>
  - Outputs: <what the user sees, charts, tables, downloads>

- <Page name>: <layout summary>
  - Inputs: <...>
  - Persists: <...>
  - Outputs: <...>

## Data

- Sources: <db, file, api, with table or endpoint names if known>
- Schema: <key tables and columns the app depends on>
- Volume: <expected rows, refresh frequency, latency budget>
- Caching: <which queries are cacheable, TTL hints>

## Auth & Access

- Sign-in: <how users authenticate, or "no auth">
- Roles: <role names and what each can see or do>
- Row-level filtering: <if users see different slices of data>

## Secrets

- <secret name>: <where it comes from, how it is consumed>
- Storage: <Streamlit secrets, env vars, secret manager>

## Theme

- Primary color: <hex or brand name>
- Mode: <light, dark, follow-system>
- Typography: <font family or stay default>
- Brand assets: <logo path, favicon, image guidelines>

## Components

- Reusable widgets: <list shared components or "none yet">
- Templates to start from: <e.g. snowflake dashboard template>

## File Structure

```
app.py              # entry point
pages/              # multipage app pages
components/         # reusable widgets
data/               # sample or static data
.streamlit/         # config and theme
```

## Performance

- Caching strategy: <data vs resource, TTL guidance>
- Fragments: <which sections re-run independently>
- Forms: <where to batch reruns>
- Expected scale: <concurrent users, data size>

## Error Handling

- Empty data: <what the user sees>
- Network or query failure: <fallback UI, retry guidance>
- Permission denied: <message and next step>

## Observability

- Logging: <what events to log, where>
- Telemetry: <metrics to track, if any>

## Dependencies

- Python: <version>
- Required packages: <streamlit, plus others with pinned versions if known>
- Optional packages: <only if a feature is enabled>

## Deployment

- Target: <Streamlit Community Cloud, Streamlit in Snowflake, custom host>
- Environment: <warehouse, container, region>
- CI/CD: <how the app gets deployed, or "manual">

## Out of Scope

> Make non-goals explicit. Prevents the agent from adding things you do not want.

- <feature or behavior the app should NOT include>
- <integration the app should NOT attempt>

## Open Questions

> Decisions deferred. The agent should ask before making assumptions here.

- <question, with current best guess if any>

## Changelog

- <YYYY-MM-DD>: initial draft
