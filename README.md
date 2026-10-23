# Public receipt audits

Reproduce the findings from saved public evidence, using standard-library
commands and exact integer arithmetic.

- [Q33 holder, treasury and reward-retention audit](q33-flapjax-20261021/README.md):
  reconcile the full holder list, classify top holders, check treasury flows and
  compare payout recipients' retained balances at a named BSC snapshot.
- [Q35 buyback audit](q35-flapjax-20261020/README.md): check buyback transactions,
  amounts and timing against the stated policy.
- [TaskMarket unsigned-message comparison](taskmarket-signature-20261021/README.md):
  compare the official legacy and v2 message formats offline without a live wallet.

- [Q41 buyback and rule audit](q41-flapjax-20261023/README.md): October 9–21 COT,
  with exact prices, native-value accounting and serial cold replay.

Each package includes its source, evidence boundaries and replay instructions.
Start with its README. A reproduced result is not a requester award or payment.

Maintained by [SameDayDesk](https://samedaydesk.com).
