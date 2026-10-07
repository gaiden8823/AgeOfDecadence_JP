"""Read-only Torque DSO 48 decoder, checked against boundaries and relocations.

Reference: Torque3D v3.8 console/compiler.h and console/codeBlock.cpp.
Failure is explicit; unknown opcodes are never guessed or skipped.
"""
import struct
from dataclasses import dataclass

NAMES = '''FUNC_DECL CREATE_OBJECT ADD_OBJECT END_OBJECT FINISH_OBJECT
JMPIFFNOT JMPIFNOT JMPIFF JMPIF JMPIFNOT_NP JMPIF_NP JMP
RETURN RETURN_VOID RETURN_FLT RETURN_UINT
CMPEQ CMPGR CMPGE CMPLT CMPLE CMPNE XOR MOD BITAND BITOR NOT NOTF ONESCOMPLEMENT SHR SHL AND OR ADD SUB MUL DIV NEG
SETCURVAR SETCURVAR_CREATE SETCURVAR_ARRAY SETCURVAR_ARRAY_CREATE
LOADVAR_UINT LOADVAR_FLT LOADVAR_STR LOADVAR_VAR SAVEVAR_UINT SAVEVAR_FLT SAVEVAR_STR SAVEVAR_VAR
SETCUROBJECT SETCUROBJECT_NEW SETCUROBJECT_INTERNAL SETCURFIELD SETCURFIELD_ARRAY SETCURFIELD_TYPE
LOADFIELD_UINT LOADFIELD_FLT LOADFIELD_STR SAVEFIELD_UINT SAVEFIELD_FLT SAVEFIELD_STR
STR_TO_UINT STR_TO_FLT STR_TO_NONE FLT_TO_UINT FLT_TO_STR FLT_TO_NONE UINT_TO_FLT UINT_TO_STR UINT_TO_NONE COPYVAR_TO_NONE
LOADIMMED_UINT LOADIMMED_FLT TAG_TO_STR LOADIMMED_STR DOCBLOCK_STR LOADIMMED_IDENT
CALLFUNC_RESOLVE CALLFUNC ADVANCE_STR ADVANCE_STR_APPENDCHAR ADVANCE_STR_COMMA ADVANCE_STR_NUL REWIND_STR TERMINATE_REWIND_STR COMPARE_STR
PUSH PUSH_UINT PUSH_FLT PUSH_VAR PUSH_FRAME ASSERT BREAK ITER_BEGIN ITER_BEGIN_STR ITER ITER_END INVALID'''.split()

def decode_text(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp1252', errors='strict')

@dataclass
class Instruction:
    ip: int
    op: str
    args: list
    table: int
    function: str
    identifier: str = ''
    string_offset: int | None = None
    text: str | None = None

class DSO:
    def __init__(self, b):
        self.b = b
        p = 0
        def u32():
            nonlocal p
            v = struct.unpack_from('<I', b, p)[0]; p += 4
            return v
        if u32() != 48:
            raise ValueError('unsupported DSO version')
        self.tables, self.bases = [], []
        for _ in range(2):
            n = u32(); self.bases.append(p); self.tables.append(b[p:p+n]); p += n
        self.float_counts = []
        for _ in range(2):
            n = u32(); self.float_counts.append(n); p += n*8
        n, linecount = u32(), u32()
        self.code = []
        for _ in range(n):
            v = b[p]; p += 1
            self.code.append(u32() if v == 255 else v)
        self.lines = [(u32(), u32()) for _ in range(linecount)]
        self.ids = {}
        self.id_offsets = {}
        for _ in range(u32()):
            offset, count = u32(), u32()
            name = self.text(0, offset)
            for _ in range(count):
                ip = u32()
                if ip in self.ids:
                    raise ValueError('duplicate identifier relocation')
                self.ids[ip] = name
                self.id_offsets[ip] = offset
        if p != len(b):
            raise ValueError('file not fully consumed')
        self.instructions = self.disassemble()

    def text(self, table, offset):
        t = self.tables[table]
        if not 0 <= offset < len(t):
            raise ValueError(f'string offset outside table {table}:{offset}')
        return decode_text(t[offset:t.index(b'\0', offset)])

    def disassemble(self):
        c = self.code
        ip, function_end, function = 0, 0, ''
        result, identifier_operands, jumps = [], set(), []
        single_arg = {'ADD_OBJECT', 'END_OBJECT', 'JMPIFFNOT', 'JMPIFNOT', 'JMPIFF', 'JMPIF', 'JMPIFNOT_NP', 'JMPIF_NP', 'JMP', 'SETCUROBJECT_INTERNAL', 'SETCURFIELD_TYPE', 'LOADIMMED_UINT', 'LOADIMMED_FLT', 'TAG_TO_STR', 'LOADIMMED_STR', 'DOCBLOCK_STR', 'ADVANCE_STR_APPENDCHAR', 'ASSERT', 'ITER'}
        ident_ops = {'SETCURVAR', 'SETCURVAR_CREATE', 'SETCURFIELD', 'LOADIMMED_IDENT'}
        while ip < len(c):
            if ip >= function_end:
                function = ''
            start = ip
            if not 0 <= c[ip] < len(NAMES)-1:
                raise ValueError(f'unknown opcode {c[ip]} at {ip}')
            op = NAMES[c[ip]]
            ip += 1
            count = 0
            positions = []
            if op == 'FUNC_DECL':
                argc = c[ip+8]
                if argc > 1024:
                    raise ValueError('invalid argument count')
                count = 9+argc*2
                positions = [ip, ip+2, ip+4] + [ip+9+j*2 for j in range(argc)]
                function_end = c[ip+7]
                function = self.ids.get(ip+2, '') + '::' + self.ids.get(ip, '')
                jumps.append(function_end)
            elif op == 'CREATE_OBJECT':
                count, positions = 7, [ip]
                jumps.append(c[ip+6])
            elif op in ident_ops:
                count, positions = 2, [ip]
            elif op in {'CALLFUNC', 'CALLFUNC_RESOLVE'}:
                count, positions = 5, [ip, ip+2]
            elif op in {'ITER_BEGIN', 'ITER_BEGIN_STR'}:
                count, positions = 3, [ip]
                jumps.append(c[ip+2])
            elif op in single_arg:
                count = 1
            if ip+count > len(c):
                raise ValueError('truncated instruction')
            identifier_operands.update(positions)
            if any(c[j:j+2] != [0,0] for j in positions):
                raise ValueError(f'nonzero unrelocated identifier at {start}')
            ins = Instruction(start, op, c[ip:ip+count], 1 if function and op != 'FUNC_DECL' else 0, function, self.ids.get(ip, ''))
            if op in {'LOADIMMED_STR', 'TAG_TO_STR', 'DOCBLOCK_STR', 'ASSERT'}:
                ins.string_offset = c[ip]
                ins.text = self.text(ins.table, c[ip])
            if op == 'LOADIMMED_FLT' and c[ip] >= self.float_counts[ins.table]:
                raise ValueError('invalid float index')
            if op.startswith('JMP') or op == 'ITER':
                jumps.append(c[ip])
            result.append(ins)
            ip += count
        boundaries = {i.ip for i in result} | {len(c)}
        if any(j not in boundaries for j in jumps):
            raise ValueError('jump does not target an instruction boundary')
        if any(ip not in boundaries for _, ip in self.lines):
            raise ValueError('line marker does not target an instruction boundary')
        if not set(self.ids).issubset(identifier_operands):
            raise ValueError('identifier relocation outside identifier operands')
        return result

if __name__ == '__main__':
    import json
    import zipfile
    from pathlib import Path
    base = Path(r'C:\GameModding\AgeOfDecadence_JP\source')
    passed, failed = [], []
    for archive in ['scripts.aod', 'art/gui.aod']:
        with zipfile.ZipFile(base / archive) as z:
            for path in z.namelist():
                if path.endswith('.dso') and ('.english.' in path or not any('.'+lang+'.' in path for lang in ['french','russian','polish','spanish','japanese'])):
                    try:
                        d = DSO(z.read(path))
                        passed.append((archive, path, len(d.instructions)))
                    except (ValueError, IndexError, struct.error, UnicodeError) as e:
                        failed.append((archive, path, str(e)))
    print(json.dumps({'passed':len(passed), 'failed':len(failed), 'first_failures':failed[:12], 'first_successes':passed[:5]},ensure_ascii=False,indent=2))
