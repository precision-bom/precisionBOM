# PrecisionBOM Blockchain

ERC-7827 smart contract implementation for immutable JSON state with version history.

## Overview

This contract implements [EIP-7827](https://eips.ethereum.org/EIPS/eip-7827) - a standard for JSON contracts with Value Version Control (VVC). It provides:

- **Immutable audit trails** for sourcing decisions
- **Version history** for all state changes
- **Access control** via authorized signer

## Contract

### ERC7827.sol

Protected implementation of EIP-7827 for invoicing and BOM records.

```solidity
interface IERC7827 {
    function json() external view returns (string memory);
    function version(string calldata key) external view returns (string[] memory);
    function write(string[] calldata keys, string[] calldata values) external;
}
```

**Functions:**
- `json()` - Returns current JSON state as a string
- `version(key)` - Returns history of values for a given key
- `write(keys, values)` - Write new key-value pairs (signer only)

## Getting Started

### Prerequisites
- Node.js 18+
- Hardhat

### Installation

```bash
npm install
```

### Compile

```bash
npx hardhat compile
```

### Test

```bash
npx hardhat test
```

### Deploy

```bash
npx hardhat run scripts/deploy.cjs --network <network>
```

## Scripts

| Script | Description |
|--------|-------------|
| `deploy.cjs` | Deploy ERC7827 contract |
| `write.cjs` | Write data to contract |
| `grant_access.cjs` | Grant signer access |
| `set_subscription.cjs` | Configure subscription |
| `test_gatekeeper.cjs` | Test gatekeeper integration |

## Configuration

Edit `hardhat.config.cts` for network settings:

```typescript
const config: HardhatUserConfig = {
  solidity: "0.8.12",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

## Usage

### Writing Data

```javascript
const keys = ["invoice_id", "total", "status"];
const values = ["INV-001", "1500.00", "approved"];
await contract.write(keys, values);
```

### Reading State

```javascript
const state = await contract.json();
// {"invoice_id": "INV-001", "total": "1500.00", "status": "approved"}
```

### Getting History

```javascript
const history = await contract.version("status");
// ["pending", "reviewed", "approved"]
```

## Security

- Only the designated `signer` address can call `write()`
- All writes are permanently recorded on-chain
- Version history is append-only and immutable
