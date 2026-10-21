# TaskMarket unsigned-message comparison

Compare the official legacy and v2 withdrawal-address message bytes without a
real wallet, an account login or a TaskMarket write. This is an offline diagnostic,
not a workaround, a withdrawal client or proof of a server defect.

## What was checked

On October21,2026, the pinned official1.13.2 and1.20.0 message builders and
signing/command wrappers both produced signatures recoverable to disposable test
identities offline. The42 controls comprise37 Node tests and five preparation
tests, independently rerun from a clean source export with no skips.

Legacy uses a destination-only message. V2 binds wallet, destination, chain,
nonce and expiry in six LF-delimited lines, without a trailing newline. The v2
builder first appeared in1.18.0, published October17;1.20.0 was published
October20. Those dates do not identify the format a deployed setter accepts.

The observed live OpenAPI still described three request fields. That mismatch
does not establish the deployed verifier, reproduce a particular401 or justify
a downgrade. The next decisive evidence is the setter's actual verifier format.
The production health response observed October21 identified commit
`375481ee01186e14893268e3817a58b011c5031c`; this repository does not contain
that server source.

## Use

Requires Node22 with its permission flag, Python3, npm and Bash.

```sh
cd taskmarket-signature-20261021
bash ./prepare.sh
bash ./test.sh
bash ./inspect.sh < unsigned-example.json
```

Preparation downloads the two integrity-pinned official npm archives and locked
dependencies, with install scripts disabled. Testing and inspection then work
offline. The inspector accepts only unsigned fields and reports the message,
UTF8 bytes and EIP191 digest for each version. It never asks for a private key
or accepts a signature field. Do not send a live or reusable signature.

Tests use the publicly known disposable scalar1/2 identities. Never fund or use
those identities for an account. No signing request or setter POST is made to
TaskMarket. The command transport is a fake fetch boundary, not live-server
acceptance, nonce replay protection or an installed CLI test.

Source archive/member/excerpt pins are in SOURCES.json. Preparation refuses
missing or modified offline archives; the controls include recovery after a
tampered cached archive. Caches and dependencies stay in ignored .scratch/.

## Primary sources

- [Official CLI documentation](https://docs.taskmarket.dev/reference/cli)
- [Official withdrawal API](https://docs.taskmarket.dev/reference/withdrawal-address)
- [Live OpenAPI](https://api.taskmarket.dev/openapi.json)
- [Official npm package and publish dates](https://registry.npmjs.org/@lucid-agents/taskmarket)

Maintained by SameDayDesk. A passing diagnostic is useful comparison evidence,
not a claim that anyone's withdrawal failure has been repaired.
