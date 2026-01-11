// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

/**
 * @title IERC7827
 * @dev Standard Interface for JSON Contract with Value Version Control (VVC).
 */
interface IERC7827 {
    function json() external view returns (string memory);
    function version(string calldata key) external view returns (string[] memory);
    function length(string calldata key) external view returns (uint256);
    function write(string[] calldata keys, string[] calldata values) external;
}

/**
 * @title ERC7827
 * @dev Standard implementation of JSON-VVC for Forensic Repositories.
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
     * @dev Returns the current JSON state as a single string.
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
     * @dev Returns the full history of a value.
     * WARNING: Large histories can cause gas exhaustion or OOM in clients.
     */
    function version(string calldata key) external view override returns (string[] memory) {
        return _history[key];
    }

    /**
     * @dev Returns the number of versions recorded for a specific key.
     * Crucial for agentic context management and UI pagination.
     */
    function length(string calldata key) external view override returns (uint256) {
        return _history[key].length;
    }

    /**
     * @dev Protected write strike.
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
