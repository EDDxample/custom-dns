
from ctypes import LittleEndianStructure, Union, c_int16, c_uint8
from struct import pack, unpack

OPCODES = ["QUERY", "IQUERY", "STATUS", "(reserved)", "NOTIFY", "UPDATE"]
RCODES  = ["No Error", "Format Error", "Server Failure", "Name Error", "Not Implemented", "Refused"]
QTYPES = {
    1:   'A',
    # 2:   'NS     (authoritative name server)',
    # 3:   'MD     (mail destination (Obsolete - use MX))',
    # 4:   'MF     (mail forwarder (Obsolete - use MX))',
    # 5:   'CNAME  (canonical name for an alias)',
    # 6:   'SOA    (start of a zone of authority)',
    # 7:   'MB     (mailbox domain name (EXPERIMENTAL))',
    # 8:   'MG     (mail group member (EXPERIMENTAL))',
    # 9:   'MR     (mail rename domain name (EXPERIMENTAL))',
    # 10:  'NULL   (null RR (EXPERIMENTAL))',
    # 11:  'WKS    (well known service description)',
    # 12:  'PTR    (domain name pointer)',
    # 13:  'HINFO  (host information)',
    # 14:  'MINFO  (mailbox or mail list information)',
    # 15:  'MX     (mail exchange)',
    # 16:  'TXT    (text strings)',
    28: 'AAAA',
    # 252: 'AXFR   (request for a transfer of an entire zone)',
    # 253: 'MAILB  (request for mailbox-related records (MB, MG or MR))',
    # 254: 'MAILA  (request for mail agent RRs (Obsolete - see MX))',
    255: '*',
}

QCLASS = {
    1:   'IN     (the internet)',
    2:   'CS     (CSNET class (Obsolete))',
    3:   'CH     (CHAOS)',
    4:   'HS     (Hesiod [Dyer 87])',
    255: '*      (any class)',
}


class HeaderBitFlags(Union):
    class BitFlags(LittleEndianStructure):
        # The fields are reorganized to adjust to the big-endian deserialization
        _fields_ = [
            ('ra',     c_uint8, 1), # Recursion Available
            ('z',      c_uint8, 3), # Zero
            ('rcode',  c_uint8, 4), # Response Code

            ('qr',     c_uint8, 1), # Query/Response Flag
            ('opcode', c_uint8, 4), # Opcode (values (0-5): QUERY, IQUERY, STATUS, (reserved), NOTIFY, UPDATE)
            ('aa',     c_uint8, 1), # Authoritative Answer Flag
            ('tc',     c_uint8, 1), # Truncation Flag
            ('rd',     c_uint8, 1), # Recursion Desired
        ]
    
    _fields_ = [('b', BitFlags), ('asbytes', c_int16)]


class DNSPacket:
    def __init__(self, data: bytes) -> None:
        # header
        self.bitflags = HeaderBitFlags()
        self.transaction_id, \
        self.bitflags.asbytes, \
        self.question_count, \
        self.answer_rrs_count, \
        self.authority_rrs_count, \
        self.additional_rrs_count = unpack('>HHHHHH', data[:12])
        self.questions = []
        self.responses = []

        # questions
        offset = 12

        for _ in range(self.question_count):
            domain_segments = []

            while data[offset]:
                length  = int.from_bytes(data[offset:offset + 1], 'big') ; offset += 1
                segment = data[offset:offset + length].decode()          ; offset += length
                domain_segments.append(segment)

            domain = '.'.join(domain_segments) + '.'

            offset += 1 # null-terminated
            qtype, qclass = unpack('>HH', data[offset:offset+4]) ; offset += 4
            self.questions.append({
                'domain': domain,
                'qtype': qtype,
                'qclass': qclass,
            })

    def compute_responses(self, zones: dict):
        """
        Hardcoded for A-IN and AAAA-IN questions
        """
        for q in self.questions:
            domain = q['domain']
            zone_data = zones.get(domain)

            if not zone_data:
                raise LookupError(f'{domain} zone file not found')

            rr = {}

            if q['qtype'] not in (1, 28):
                raise NotImplementedError(f'QUESTION TYPE: {q["qtype"]}')
            if q['qclass'] != 1:
                raise NotImplementedError(f'QUESTION CLASS: {q["qclass"]}')

            rr['type']  = q['qtype']
            rr['class'] = q['qclass']
            
            for a in zone_data[QTYPES[q['qtype']]]:
                rr = {**rr, **a}
                self.responses.append(rr)


    def serialize(self) -> bytes:
        out = b''

        outflags = HeaderBitFlags()
        outflags.asbytes = self.bitflags.asbytes
        outflags.b.qr = 1

        out += pack('>HHHHHH', self.transaction_id, outflags.asbytes, self.question_count, self.answer_rrs_count + len(self.responses), self.authority_rrs_count, self.additional_rrs_count)

        for q in self.questions:
            # the null byte at the end is handled here due to the final dot (google.com. -> [google, com, ])
            for segment in q['domain'].split('.'):
                segment: str
                out += len(segment).to_bytes(1, 'big')
                out += segment.encode()
            out += pack('>HH', q['qtype'], q['qclass'])

        for r in self.responses:
            out += len(r['name']).to_bytes(1, 'big')
            out += r['name'].encode() + b'\x00'
            out += r['type'].to_bytes(2, 'big')
            out += r['class'].to_bytes(2, 'big')
            out += r['ttl'].to_bytes(4, 'big')

            # A (IPv4) record
            if r['type'] == 1:
                out += (4).to_bytes(2, 'big')

                for segment in r['value'].split('.'):
                    out += int(segment).to_bytes(1, 'big')

            # AAAA (IPv6) record
            elif r['type'] == 28:
                out += (16).to_bytes(2, 'big')

                for segment in r['value'].split(':'):
                    out += int(segment, 16).to_bytes(2, 'big')

            else:
                raise NotImplementedError(f'RESPONSE TYPE: {r["type"]}')

        return out
