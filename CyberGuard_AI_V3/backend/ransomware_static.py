"""Static PE features shared by the local training data and file extractor."""
import struct
from backend.pe_features import extract_pe

FEATURES = ['SizeOfCode', 'SizeOfInitializedData', 'SizeOfUninitializedData',
            'BaseOfCode', 'BaseOfData', 'ImageBase', 'SizeOfImage', 'SizeOfHeaders',
            'SectionAlignment', 'FileAlignment', 'Checksum', 'SizeofStackReserve',
            'SizeofStackCommit', 'SizeofHeapCommit', 'SizeofHeapReserve', 'LoaderFlags']


def extract(data):
    base = extract_pe(data)
    opt = struct.unpack_from('<I', data, 60)[0] + 24
    wide = struct.unpack_from('<H', data, opt)[0] == 0x20b
    values = {n: base[n] for n in FEATURES[:8]}
    for name, offset in [('SectionAlignment', 32), ('FileAlignment', 36), ('Checksum', 64)]:
        values[name] = struct.unpack_from('<I', data, opt + offset)[0]
    for i, name in enumerate(['SizeofStackReserve', 'SizeofStackCommit', 'SizeofHeapReserve', 'SizeofHeapCommit']):
        values[name] = struct.unpack_from('<Q' if wide else '<I', data, opt + 72 + i * (8 if wide else 4))[0]
    values['LoaderFlags'] = struct.unpack_from('<I', data, opt + (104 if wide else 88))[0]
    return {n: float(values[n]) for n in FEATURES}
