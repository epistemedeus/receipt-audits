import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = fileURLToPath(new URL('.', import.meta.url));
const require = createRequire(root + '.scratch/deps/package.json');
const { privateKeyToAccount } = require('viem/accounts');
const { recoverMessageAddress, getAddress, hashMessage, keccak256, toHex } = require('viem');
// PUBLIC, DISPOSABLE test scalar 1. Never fund or use as an account.
const account = privateKeyToAccount('0x' + '0'.repeat(63) + '1');
const other = privateKeyToAccount('0x' + '0'.repeat(63) + '2');
assert.equal(account.address, '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf');
const input = {
  walletAddress: account.address,
  withdrawalAddress: getAddress('0xabcdefabcdefabcdefabcdefabcdefabcdefabcd'),
  chainId: 8453, nonce: '0x' + 'AB'.repeat(32), expiresAt: 1700000000,
};
const sources = Object.fromEntries(['1.13.2', '1.20.0'].map(v => [v,
  JSON.parse(readFileSync(root + '.scratch/' + v + '-source.json', 'utf8'))]));
const builders = {};
const signers = {};
for (const [version, source] of Object.entries(sources)) {
  // Execute only the integrity-checked pure builder and exact signing wrapper.
  const context = vm.createContext({ createWalletAccountFromKeystore: async store => {
    assert.equal(store.synthetic, true);
    return account;
  }});
  vm.runInContext(source.builder + '\n' + source.signer, context, { timeout: 1000 });
  builders[version] = context.buildSetWithdrawalAddressMessage;
  signers[version] = message => context.signMessage(message, { synthetic: true });
}
const legacy = x => builders['1.13.2'](x.withdrawalAddress);
const v2 = x => builders['1.20.0'](x);
const matches = async (message, signature, wallet = account.address) =>
  getAddress(await recoverMessageAddress({ message, signature })) === getAddress(wallet);

test('actual builders produce byte-exact legacy and six-line v2 messages', () => {
  assert.equal(legacy(input), 'taskmarket:set-withdrawal-address:' + input.withdrawalAddress.toLowerCase());
  assert.equal(v2(input), [
    'Taskmarket: set withdrawal address v2', 'Wallet: ' + account.address.toLowerCase(),
    'Withdrawal address: ' + input.withdrawalAddress.toLowerCase(), 'Chain: 8453',
    'Nonce: 0x' + 'ab'.repeat(32), 'Expires: 1700000000',
  ].join('\n'));
  assert.equal(v2(input).split('\n').length, 6);
  assert.ok(!v2(input).endsWith('\n'));
});
for (const [version, build] of [['1.13.2', legacy], ['1.20.0', v2]]) {
  test(version + ' exact source wrapper signs EIP-191 and recovers expected signer', async () => {
    const message = build(input);
    const signature = await signers[version](message);
    assert.ok(await matches(message, signature));
    assert.ok(!await matches(message, signature, other.address));
    // EIP-191 prefix contains the UTF-8 BYTE count, then raw message bytes.
    const bytes = Buffer.from(message, 'utf8');
    const explicit = Buffer.concat([Buffer.from('\x19Ethereum Signed Message:\n' + bytes.length), bytes]);
    assert.equal(hashMessage(message), keccak256(toHex(explicit)));
  });
  test(version + ' destination casing normalizes to the same signed bytes', async () => {
    const lower = { ...input, withdrawalAddress: input.withdrawalAddress.toLowerCase() };
    assert.equal(build(input), build(lower));
    assert.ok(await matches(build(lower), await signers[version](build(input))));
  });
  test(version + ' changed destination invalidates signer comparison', async () => {
    assert.ok(!await matches(build({ ...input, withdrawalAddress: other.address }), await signers[version](build(input))));
  });
  test(version + ' hex-text signing and double-prefix/prehash signing differ from UTF-8 signing', async () => {
    const message = build(input);
    const hexTextSignature = await signers[version](toHex(Buffer.from(message)));
    assert.ok(!await matches(message, hexTextSignature));
    const prehashSignature = await account.signMessage({ message: { raw: hashMessage(message) } });
    assert.ok(!await matches(message, prehashSignature));
    // Wallet raw UTF-8 bytes are equivalent to the original UTF-8 string.
    assert.ok(await matches(message, await account.signMessage({ message: { raw: toHex(Buffer.from(message)) } })));
  });
  test(version + ' malformed signature fails; fresh valid signature recovers', async () => {
    await assert.rejects(matches(build(input), '0x1234'));
    assert.ok(await matches(build(input), await signers[version](build(input))));
  });
}
test('legacy and v2 signatures are incompatible in both directions', async () => {
  assert.ok(!await matches(v2(input), await signers['1.13.2'](legacy(input))));
  assert.ok(!await matches(legacy(input), await signers['1.20.0'](v2(input))));
});
test('v2 wallet casing and nonce casing normalize', () => {
  assert.equal(v2(input), v2({ ...input, walletAddress: input.walletAddress.toLowerCase(), nonce: input.nonce.toLowerCase() }));
});
for (const [field, value] of [['walletAddress', other.address], ['chainId', 42161], ['nonce', '0x' + '12'.repeat(32)], ['expiresAt', input.expiresAt + 1]]) {
  test('v2 changed ' + field + ' invalidates signer comparison', async () => {
    assert.ok(!await matches(v2({ ...input, [field]: value }), await signers['1.20.0'](v2(input))));
  });
}
for (const [name, change] of [['CRLF', s => s.replaceAll('\n', '\r\n')], ['trailing LF', s => s + '\n'], ['literal slash-n', s => s.replaceAll('\n', '\\n')], ['UTF-8 BOM', s => '\ufeff' + s]]) {
  test('v2 ' + name + ' changes signed bytes', async () => {
    assert.ok(!await matches(change(v2(input)), await signers['1.20.0'](v2(input))));
  });
}
test('legacy does not bind wallet/chain/nonce/expiry; signer equality remains required', async () => {
  const altered = { ...input, walletAddress: other.address, chainId: 1, nonce: 'changed', expiresAt: 0 };
  assert.equal(legacy(input), legacy(altered));
  assert.ok(!await matches(legacy(altered), await signers['1.13.2'](legacy(input)), altered.walletAddress));
});
test('expiry cryptographic binding is separate from server time/replay enforcement', async () => {
  const expired = v2({ ...input, expiresAt: 1 });
  assert.ok(await matches(expired, await signers['1.20.0'](expired)));
});

function commandHarness(version, fault) {
  const calls = { loads: 0, signs: 0, posts: [], errors: [], pins: 0, remembered: [] };
  let action;
  class Command {
    description() { return this; } argument() { return this; }
    action(fn) { action = fn; return this; }
  }
  const context = vm.createContext({
    Command48: Command, Command56: Command,
    loadKeystore: async () => { calls.loads++; if (fault === 'load') throw Error('synthetic unavailable'); return { walletAddress: account.address }; },
    selectedNetwork: () => ({ chainId: 8453 }),
    randomBytes2: () => Buffer.from('ab'.repeat(32), 'hex'), SIGNATURE_TTL_SECONDS: 300,
    Date: class extends Date { static now() { return 1699999700000; } },
    signMessage: async message => { calls.signs++; if (fault === 'sign') throw Error('synthetic signer unavailable'); return signers[version](message); },
    API_URL: 'https://offline.invalid', apiUrl: () => 'https://offline.invalid',
    legalReceiptHeaders: async () => ({}),
    resolveIdempotencyKey: key => key ?? 'synthetic',
    idempotencyHeaders: key => ({ 'Idempotency-Key': key }),
    rememberIdempotencyKeyFor: (_error, key) => calls.remembered.push(key),
    ApiError: class extends Error {
      constructor(status, message, key) { super(message); this.status = status; this.idempotencyKey = key; }
    },
    readFailureBody: async () => ({ body: { error: 'synthetic 401' } }),
    failureMessage: () => 'synthetic 401', apiErrorEnvelopeOf: () => undefined,
    fetch: async (url, options) => {
      assert.equal(url, 'https://offline.invalid/api/wallet/set-withdrawal-address');
      assert.equal(options.method, 'POST'); assert.equal(options.redirect, 'error');
      assert.equal(options.headers['Idempotency-Key'], 'synthetic');
      const body = JSON.parse(options.body);
      calls.posts.push({ path: '/api/wallet/set-withdrawal-address', body });
      if (fault === 'network') throw Error('synthetic transport unavailable');
      if (fault === 'post') return { ok: false, status: 401 };
      return { ok: true, json: async () => ({ chainId: 8453, withdrawalAddress: body.withdrawalAddress, accountRecoveryCode: '00000000' }) };
    },
    serverChainMismatch: () => undefined,
    pinWithdrawalAddress: async () => { calls.pins++; },
    printResult: () => {}, printError: e => calls.errors.push(e),
  });
  vm.runInContext([sources[version].builder, sources[version].validator, sources[version].idempotent, sources[version].transport, sources[version].command].join('\n'), context, { timeout: 1000 });
  return { calls, run: address => action(address) };
}
for (const version of Object.keys(sources)) {
  test(version + ' actual transport preserves unknown network failure without retry', async () => {
    const broken = commandHarness(version, 'network');
    await assert.rejects(broken.run(input.withdrawalAddress), /synthetic transport unavailable/);
    assert.equal(broken.calls.posts.length, 1);
    assert.deepEqual(broken.calls.remembered, ['synthetic']);
  });
  test(version + ' actual command emits source-consistent payload to MOCK transport', async () => {
    const { calls, run } = commandHarness(version);
    await run(input.withdrawalAddress);
    assert.equal(calls.posts.length, 1);
    const { path, body } = calls.posts[0];
    assert.equal(path, '/api/wallet/set-withdrawal-address');
    assert.deepEqual(Object.keys(body).sort(), (version === '1.13.2'
      ? ['walletAddress', 'withdrawalAddress', 'signature']
      : ['walletAddress', 'withdrawalAddress', 'signature', 'chainId', 'nonce', 'expiresAt']).sort());
    assert.equal(body.withdrawalAddress, input.withdrawalAddress);
    assert.ok(await matches(version === '1.13.2' ? legacy(body) : v2(body), body.signature));
    assert.equal(calls.pins, version === '1.20.0' ? 1 : 0);
  });
  test(version + ' command invalid destination stops before store/sign/transport', async () => {
    const { calls, run } = commandHarness(version);
    await run('bad');
    assert.equal(calls.loads, 0); assert.equal(calls.signs, 0); assert.equal(calls.posts.length, 0);
    assert.equal(calls.errors.length, 1);
  });
  test(version + ' command missing synthetic store stops before sign/transport', async () => {
    const { calls, run } = commandHarness(version, 'load');
    await run(input.withdrawalAddress);
    assert.equal(calls.signs, 0); assert.equal(calls.posts.length, 0); assert.equal(calls.errors.length, 1);
  });
  test(version + ' signer failure sends no request', async () => {
    const { calls, run } = commandHarness(version, 'sign');
    await assert.rejects(run(input.withdrawalAddress), /synthetic signer unavailable/);
    assert.equal(calls.posts.length, 0);
  });
  test(version + ' failed MOCK post is not retried; separate healthy invocation works', async () => {
    const broken = commandHarness(version, 'post');
    await assert.rejects(broken.run(input.withdrawalAddress), /synthetic 401/);
    assert.equal(broken.calls.posts.length, 1); assert.equal(broken.calls.pins, 0);
    assert.deepEqual(broken.calls.remembered, ['synthetic']);
    const healthy = commandHarness(version);
    await healthy.run(input.withdrawalAddress);
    assert.equal(healthy.calls.posts.length, 1);
  });
}

const { inspect } = await import('./inspect.mjs');
test('unsigned inspector compares exact source bytes and distinguishes versions', () => {
  const result = inspect({ ...input, message: v2(input) });
  assert.equal(result['1.13.2'].matchesProvidedMessage, false);
  assert.equal(result['1.20.0'].matchesProvidedMessage, true);
  assert.equal(result['1.20.0'].eip191Digest, hashMessage(v2(input)));
});
test('unsigned inspector rejects signature/key fields and malformed unsigned values', () => {
  for (const extra of [{ signature: '0x1234' }, { privateKey: 'forbidden' }]) assert.throws(() => inspect({ ...input, ...extra }), /unsigned/);
  for (const extra of [{ chainId: 0 }, { expiresAt: 1.5 }, { nonce: 'bad' }, { walletAddress: 'bad' }]) assert.throws(() => inspect({ ...input, ...extra }), /Invalid/);
});
