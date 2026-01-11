// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

/**
 * @title IERC7827
 * @dev Standard Interface for JSON Contract with Value Version Control.
 */
interface IERC7827 {
    function json() external view returns (string memory);
    function version(string calldata key) external view returns (string[] memory);
    function write(string[] calldata keys, string[] calldata values) external;
}

/**
 * @title ERC7827
 * @dev Protected implementation of EIP-7827 for Invoicing.
 * Only the designated 'signer' can evolve the JSON state.
 */
contract ERC7827 is IERC7827 {
    address public signer;
    
    mapping(string => string) private _state;
    mapping(string => string[]) private _history;
    string[] private _index;
    mapping(string => bool) private _active;

    /**
     * @dev Initialize the contract with the authorized party.
     */
    constructor(address _authorizedSigner) {
        signer = _authorizedSigner;
    }

    /**
     * @dev Access control to prevent unauthorized writes to the forensic record.
     */
    modifier onlySigner() {
        require(msg.sender == signer, "ERC7827: Unauthorized");
        _;
    }

    /**
     * @dev EIP-7827: Returns the current JSON state.
     */
    function json() external view override returns (string memory) {
        string memory output = "{";
        for (uint i = 0; i < _index.length; i++) {
            string memory k = _index[i];
            output = string.concat(output, '"', k, '": "', _state[k], '"');
            if (i < _index.length - 1) output = string.concat(output, ", ");
        }
        return string.concat(output, "}");
    }

    /**
     * @dev EIP-7827: Returns history of a value for Value Version Control (VVC).
     */
    function version(string calldata key) external view override returns (string[] memory) {
        return _history[key];
    }

    /**
     * @dev EIP-7827: Protected write strike.
     * Requires the transaction to be signed by the authorized 'signer'.
     */
    function write(string[] calldata keys, string[] calldata values) external override onlySigner {
        require(keys.length == values.length, "ERC7827: Array mismatch");
        
        for (uint i = 0; i < keys.length; i++) {
            string memory k = keys[i];
            string memory v = values[i];

            if (!_active[k]) {
                _index.push(k);
                _active[k] = true;
            }

            _state[k] = v;
            _history[k].push(v);
        }
    }
}
