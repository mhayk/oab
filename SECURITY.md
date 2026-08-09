# Security Policy

## Reporting a vulnerability

Report security issues privately to **security@oab.run**, or through
[GitHub private vulnerability reporting](https://github.com/mhayk/oab/security/advisories/new).

Please do not open a public issue for a security problem.

Include what you have: what you found, how to reproduce it, and what you think the impact is. A
partial report is more useful than no report.

**Response targets:**

| Stage | Target |
| :-- | :-- |
| Acknowledgement | 3 working days |
| Initial assessment | 10 working days |
| Fix or mitigation for a confirmed high-severity issue | 30 days |

We will credit you in the advisory unless you prefer otherwise.

## What is in scope

OAB is a local-first project: Markdown, JSON Schema, and standard-library Python. It has no server,
no accounts, and no telemetry. The realistic attack surface is therefore narrow but not empty.

**In scope:**

- **Prompt injection through repository content.** `/oab:review` reads files from a repository under
  analysis. Content crafted to redirect the reading agent — for example instructions embedded in a
  source comment or a README — is a genuine vulnerability class for this project, and one we want
  reported.
- **Command injection or path traversal** in `calculators/` or `tools/`, including through
  crafted arguments or file paths.
- **Malicious knowledge units** that instruct an agent to take harmful actions, exfiltrate data, or
  weaken a user's security posture.
- **Supply-chain issues** in CI workflows or the release process.
- **Plugin packaging issues** that would cause the integration to read or write outside its
  intended scope.

**Out of scope:**

- Behaviour of the AI agent itself. Report those to that vendor.
- Architecture advice you disagree with. That is an issue or a pull request, not a vulnerability —
  though advice that is actively dangerous (for example recommending disabling authentication) is
  in scope as a knowledge-quality defect and we want to hear about it.
- Vulnerabilities in software OAB merely writes *about*.
- Denial of service against a local script by feeding it absurd input.

## Supported versions

OAB is pre-1.0. Only the latest release receives fixes. Once 1.0 ships, this section will state a
support window.

## Security of the knowledge base

Knowledge units are executable instructions to an AI agent, not inert documentation. A pull request
that adds a knowledge unit is reviewed with that in mind. Reviewers check that a unit does not:

- instruct an agent to run commands unrelated to architecture analysis,
- recommend disabling security controls without a stated, bounded justification,
- contain content addressed to the agent rather than to the reader.

If you find such a unit in `main`, treat it as a security issue and report it privately.
