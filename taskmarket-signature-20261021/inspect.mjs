// Offline unsigned-message comparison. No signing and no network interfaces.
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
const root = fileURLToPath(new URL('.', import.meta.url));
const require = createRequire(root + '.scratch/deps/package.json');
const { hashMessage } = require('viem');
export function inspect(input) {
  const allowed = ['walletAddress', 'withdrawalAddress', 'chainId', 'nonce', 'expiresAt', 'message'];
  if (!input || typeof input !== 'object' || Array.isArray(input) || Object.keys(input).some(k => !allowed.includes(k))) {
    throw Error('Only unsigned message fields are accepted; signatures and keys are excluded');
  }
  for (const field of ['walletAddress', 'withdrawalAddress']) {
    if (typeof input[field] !== 'string' || !/^0x[0-9a-fA-F]{40}$/.test(input[field])) throw Error('Invalid ' + field);
  }
  if (!Number.isSafeInteger(input.chainId) || input.chainId <= 0) throw Error('Invalid chainId');
  if (!Number.isSafeInteger(input.expiresAt) || input.expiresAt < 0) throw Error('Invalid expiresAt');
  if (typeof input.nonce !== 'string' || !/^0x[0-9a-fA-F]{64}$/.test(input.nonce)) throw Error('Invalid nonce');
  if ('message' in input && typeof input.message !== 'string') throw Error('Invalid message');
  const result = {};
  for (const version of ['1.13.2', '1.20.0']) {
    const { builder } = JSON.parse(readFileSync(root + '.scratch/' + version + '-source.json', 'utf8'));
    const context = vm.createContext({});
    vm.runInContext(builder, context, { timeout: 1000 });
    const message = context.buildSetWithdrawalAddressMessage(version === '1.13.2' ? input.withdrawalAddress : input);
    result[version] = { message, utf8Hex: '0x' + Buffer.from(message).toString('hex'),
      byteLength: Buffer.byteLength(message), eip191Digest: hashMessage(message),
      ...('message' in input ? { matchesProvidedMessage: message === input.message } : {}) };
  }
  return result;
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  try { console.log(JSON.stringify(inspect(JSON.parse(readFileSync(0, 'utf8'))), null, 2)); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
