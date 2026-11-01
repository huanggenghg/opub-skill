# Third-Party Notices

## Alipay Payment Skills

The following directories are redistributed unmodified from
<https://github.com/alipay/payment-skills>:

- `bundled/alipay-payment-skill/`
- `bundled/alipay-authenticate-wallet/`

They are licensed under the Apache License, Version 2.0. The upstream license
text is included at `bundled/LICENSE-APACHE-2.0`; the upstream `LEGAL.md` is
included at `bundled/LEGAL.md`.

Each bundled skill keeps its original `.signature/` directory. `install.py`
verifies every signed file against `.signature/code-resources.json` before
copying it to the host skills directory.

The `alipay-bot` CLI is the official npm package `@alipay/agent-payment`,
installed at the version and integrity pinned in the bundled skill and in
`install.py`.
