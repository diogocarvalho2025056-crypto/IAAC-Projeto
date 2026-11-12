"""Non-executing PE32/PE32+ feature extraction, schema v1.

Definitions: section entropy uses raw bytes including file alignment padding;
Text/DataSectionSize uses SizeOfRawData of exact .text/.data sections; imports
count descriptors and non-null lookup thunks; overlay follows the last section.
These definitions must be compared with the original dataset's extractor before
claiming equivalent performance on external files.
"""
import math
import struct
from collections import Counter


class UnsupportedPE(ValueError):
    pass


def extract_pe(data: bytes) -> dict:
    def read(fmt, offset):
        size = struct.calcsize('<' + fmt)
        if offset < 0 or offset + size > len(data):
            raise UnsupportedPE('Cabeçalho PE truncado ou offset inválido.')
        values = struct.unpack_from('<' + fmt, data, offset)
        return values[0] if len(values) == 1 else values

    if data[:2] != b'MZ':
        raise UnsupportedPE('Este modelo aceita apenas executáveis Windows PE (EXE/DLL).')
    pe = read('I', 60)
    if data[pe:pe + 4] != b'PE\0\0':
        raise UnsupportedPE('A assinatura PE não é válida.')
    sections_count = read('H', pe + 6)
    optional_size = read('H', pe + 20)
    characteristics = read('H', pe + 22)
    opt = pe + 24
    magic = read('H', opt)
    if magic not in (0x10b, 0x20b):
        raise UnsupportedPE('Formato opcional PE não suportado.')
    wide = magic == 0x20b
    minimum = 112 if wide else 96
    if optional_size < minimum or opt + optional_size > len(data) or not 1 <= sections_count <= 96:
        raise UnsupportedPE('Estrutura PE inválida ou número de secções não suportado.')
    sections = []
    start = opt + optional_size
    for i in range(sections_count):
        pos = start + 40 * i
        read('I', pos + 36)
        name = data[pos:pos + 8].split(b'\0')[0]
        virtual_size, virtual_address, size, pointer = read('IIII', pos + 8)
        if size and (pointer == 0 or pointer + size > len(data)):
            raise UnsupportedPE('Secção PE truncada.')
        raw = data[pointer:pointer + size] if size else b''
        entropy = -sum((n / len(raw)) * math.log2(n / len(raw)) for n in Counter(raw).values()) if raw else 0.0
        sections.append((name, virtual_address, virtual_size, size, pointer, entropy))

    def rva_to_offset(rva):
        if rva < read('I', opt + 60) and rva < len(data):
            return rva
        for _, va, vs, size, ptr, _ in sections:
            if va <= rva < va + max(vs, size):
                delta = rva - va
                if delta < size and ptr + delta < len(data):
                    return ptr + delta
        raise UnsupportedPE('Diretório PE aponta para dados indisponíveis.')

    count = read('I', opt + (108 if wide else 92))
    directories = opt + minimum
    def directory(index):
        if count <= index:
            return (0, 0)
        if directories + 8 * (index + 1) > opt + optional_size:
            raise UnsupportedPE('Tabela de diretórios truncada.')
        return read('II', directories + index * 8)

    imported_dlls = imported_functions = 0
    import_rva, import_size = directory(1)
    if import_rva:
        base = rva_to_offset(import_rva)
        limit = min(import_size // 20, 4096)
        terminated = False
        for i in range(limit):
            desc = read('IIIII', base + i * 20)
            if not any(desc):
                terminated = True
                break
            lookup, _, _, name_rva, first = desc
            if not name_rva or not (lookup or first):
                raise UnsupportedPE('Descritor de imports inválido.')
            rva_to_offset(name_rva)
            imported_dlls += 1
            thunk = rva_to_offset(lookup or first)
            width, fmt = (8, 'Q') if wide else (4, 'I')
            for j in range(65536):
                if read(fmt, thunk + j * width) == 0:
                    break
                imported_functions += 1
            else:
                raise UnsupportedPE('Tabela de imports excede o limite.')
        if not terminated:
            raise UnsupportedPE('Tabela de imports sem terminador válido.')
    export_rva, _ = directory(0)
    exported_functions = read('I', rva_to_offset(export_rva) + 20) if export_rva else 0
    entropies = [s[5] for s in sections]
    overlay_start = max([read('I', opt + 60)] + [s[4] + s[3] for s in sections if s[3]])
    features = {name: read('I', opt + offset) for name, offset in {
        'SizeOfCode': 4, 'SizeOfInitializedData': 8, 'SizeOfUninitializedData': 12,
        'AddressOfEntryPoint': 16, 'BaseOfCode': 20, 'SizeOfImage': 56, 'SizeOfHeaders': 60,
    }.items()}
    features.update({
        'BaseOfData': 0 if wide else read('I', opt + 24),
        'ImageBase': read('Q', opt + 24) if wide else read('I', opt + 28),
        'NumberOfSections': sections_count, 'DllCharacteristics': read('H', opt + 70),
        'Characteristics': characteristics, 'Subsystem': read('H', opt + 68),
        'AvgSectionEntropy': sum(entropies) / len(entropies),
        'MaxSectionEntropy': max(entropies), 'MinSectionEntropy': min(entropies),
        'TextSectionSize': sum(s[3] for s in sections if s[0] == b'.text'),
        'DataSectionSize': sum(s[3] for s in sections if s[0] == b'.data'),
        'ImportedDLLs': imported_dlls, 'ImportedFunctions': imported_functions,
        'HasExportTable': int(bool(export_rva)), 'ExportedFunctions': exported_functions,
        'OverlaySize': max(0, len(data) - overlay_start),
    })
    return features
