from fgo.gql.types import Error, ErrorCode


def ProtocolFileMissingError(filepath):
    return Error(
        code=ErrorCode.PROTOCOL_FILE_MISSING,
        description=f"Could not generic protocol file '{filepath}'. Please run `fgo setup` on this device."
    )


def ProtocolFileHashMismatch(filepath, expected_hash, actual_hash):
    return Error(
        code=ErrorCode.PROTOCOL_FILE_HASH_MISMATCH,
        description=f"Generic protocol file hash mismatch '{filepath}', expected {expected_hash}, got {actual_hash}. Please run `fgo setup` on this device."
    )
