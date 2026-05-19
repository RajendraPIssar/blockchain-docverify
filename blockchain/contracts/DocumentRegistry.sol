// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title  DocumentRegistry
 * @notice Stores SHA-256 document hashes on the Ethereum blockchain.
 *         Once a hash is registered it can NEVER be changed or deleted.
 * @dev    Group Project — Masters in Computer Science
 */
contract DocumentRegistry {

    // ── Data structure ────────────────────────────────────────────────────────
    struct Document {
        address uploader;   // Ethereum wallet that registered the document
        uint256 timestamp;  // Unix time of registration (set by the block)
        bool    exists;     // Used to check if a hash is registered
        string  filename;   // Optional: original filename stored as metadata
    }

    // ── State ─────────────────────────────────────────────────────────────────
    // Maps a 32-byte SHA-256 hash to a Document record
    mapping(bytes32 => Document) private documents;

    // Total number of documents registered (public — anyone can read)
    uint256 public totalDocuments;

    // Contract owner (the address that deployed it)
    address public owner;

    // ── Events ─────────────────────────────────────────────────────────────────
    // Events are logged on-chain and can be indexed by block explorers
    event DocumentRegistered(
        bytes32 indexed docHash,
        address indexed uploader,
        uint256 timestamp
    );

    // ── Constructor ────────────────────────────────────────────────────────────
    constructor() {
        owner = msg.sender;
    }

    // ── Functions ──────────────────────────────────────────────────────────────

    /**
     * @notice Register a new document hash on the blockchain.
     * @param  docHash  SHA-256 hash of the document as bytes32.
     * @param  filename Original filename stored as metadata.
     *
     * Rules:
     *  - Hash cannot be all zeros.
     *  - Same hash cannot be registered twice.
     */
    function registerDocument(bytes32 docHash, string calldata filename) external {
        require(docHash != bytes32(0), "Hash cannot be zero");
        require(!documents[docHash].exists, "Document already registered");

        documents[docHash] = Document({
            uploader:  msg.sender,
            timestamp: block.timestamp,
            exists:    true,
            filename:  filename
        });

        totalDocuments += 1;
        emit DocumentRegistered(docHash, msg.sender, block.timestamp);
    }

    /**
     * @notice Check if a document hash is registered.
     * @param  docHash  SHA-256 hash to verify.
     * @return exists    true if the document was registered.
     * @return timestamp Unix time of registration.
     * @return uploader  Ethereum address that registered it.
     *
     * @dev This is a VIEW function — FREE to call. No gas. No transaction.
     */
    function verifyDocument(bytes32 docHash)
        external
        view
        returns (bool exists, uint256 timestamp, address uploader)
    {
        Document storage d = documents[docHash];
        return (d.exists, d.timestamp, d.uploader);
    }
}
