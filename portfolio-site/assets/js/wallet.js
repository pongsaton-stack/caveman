// Wallet-connect (MetaMask / any EIP-1193 provider) via ethers.js, loaded
// only when the visitor actually clicks "Connect Wallet" — most people
// browsing a portfolio site never touch this, no reason to fetch a crypto
// library for them.
//
// ethers.js is VENDORED (assets/vendor/ethers.umd.min.js), not loaded from
// a CDN. It's the exact ethers@6.13.4 dist/ethers.umd.min.js from the
// official npm tarball (npm verified its integrity on download; recorded
// sha384 at vendor time: e999743dcf338d2cfc2af98d79746f510818e2bc856fe07
// 00ef28298b61c04c1348e801aaeee3dd6d4208bd07bcec30c — re-check this if you
// ever replace the file). Serving it same-origin means there's no
// third-party CDN in the trust chain for this script at all, and no CSP
// script-src entry needed beyond 'self'. To upgrade the version: download
// the new dist/ethers.umd.min.js from the matching ethers npm package,
// verify npm's own integrity check passed, replace the vendored file, and
// update the sha384 recorded here.
//
// SECURITY NOTES (read before wiring this into anything that moves real
// money):
// - We never see or handle private keys or seed phrases. Every transaction
//   is built here but must be confirmed inside the user's own wallet
//   extension — that confirmation screen is the actual safety boundary.
// - Always validate the recipient address client-side (isValidEthAddress)
//   AND show it back to the user before sending — typo'd addresses lose
//   funds irrecoverably on most chains.
// - Test any payment flow on a testnet (e.g. Sepolia) before real mainnet
//   funds are involved. Never assume this code is production-audited.
import { isValidEthAddress } from "./render-utils.js";

const ETHERS_LOCAL_URL = new URL("../vendor/ethers.umd.min.js", import.meta.url).href;

let ethersLoadPromise = null;
let state = { provider: null, signer: null, address: null, chainName: null };
const listeners = new Set();

function loadEthers() {
  if (window.ethers) return Promise.resolve(window.ethers);
  if (!ethersLoadPromise) {
    ethersLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = ETHERS_LOCAL_URL;
      script.onload = () => resolve(window.ethers);
      script.onerror = () => reject(new Error("failed-to-load-ethers"));
      document.head.appendChild(script);
    });
  }
  return ethersLoadPromise;
}

export function hasInjectedWallet() {
  return typeof window.ethereum !== "undefined";
}

export function getWalletState() {
  return { ...state };
}

export function onWalletChange(cb) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

function notify() {
  listeners.forEach((cb) => cb(getWalletState()));
}

export async function connectWallet() {
  if (!hasInjectedWallet()) throw new Error("no-wallet");
  const ethers = await loadEthers();

  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  const address = accounts[0];
  if (!isValidEthAddress(address)) throw new Error("invalid-address-returned");

  const provider = new ethers.BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();
  const network = await provider.getNetwork();

  state = { provider, signer, address, chainName: network.name || `chain-${network.chainId}` };
  notify();

  window.ethereum.on?.("accountsChanged", (accts) => {
    if (!accts.length) {
      disconnectWallet();
    } else {
      state.address = accts[0];
      notify();
    }
  });
  window.ethereum.on?.("chainChanged", () => window.location.reload());

  return getWalletState();
}

export function disconnectWallet() {
  state = { provider: null, signer: null, address: null, chainName: null };
  notify();
}

export async function getBalanceEth() {
  if (!state.provider || !state.address) throw new Error("not-connected");
  const ethers = await loadEthers();
  const raw = await state.provider.getBalance(state.address);
  return ethers.formatEther(raw);
}

export async function sendPaymentEth(toAddress, amountEth) {
  if (!state.signer) throw new Error("not-connected");
  if (!isValidEthAddress(toAddress)) throw new Error("invalid-recipient");
  const amount = Number(amountEth);
  if (!Number.isFinite(amount) || amount <= 0) throw new Error("invalid-amount");

  const ethers = await loadEthers();
  const tx = await state.signer.sendTransaction({
    to: toAddress,
    value: ethers.parseEther(String(amount))
  });
  return tx.hash;
}
