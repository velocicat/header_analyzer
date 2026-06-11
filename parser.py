import email
import re

import datetime as dt

from dataclasses import dataclass, field

re_group_parens = r'(\(.*?\))'

class EmailHeader:
    def __init__(self, raw_text):
        self._raw = raw_text.strip()
        self._mime_msg = email.message_from_string(self._raw)

        self.sender_info = self.get_sender_info()
        self.authentication_info = self.get_authentication_info(self._mime_msg.get('authentication-results'))
        self.routing_info = self.get_routing_info(self._mime_msg.get_all('received'))

    def get_sender_info(self):
        return SenderInfo(self._mime_msg)
    
    def get_authentication_info(self, raw):
        return AuthenticationInfo.from_header(raw)
    
    def get_routing_info(self, raw):
        raw_hops = list(reversed(raw) or [])
        return [RoutingHop(hop) for hop in raw_hops]
    
    # TODO Input validation, handle get_all situations, standardize output
    def get_header_value(self, header_name):
        return self._mime_msg.get(header_name)
    
    def get_all_headers(self):
        return self._mime_msg.items()

class SenderInfo:
    NOTES = {
        "from": "(P2) - Header From, Display From, RFC5322.From - Shows as from in the users email client",
        "reply-to": "Where replies go to",
        "return-path": "(P1) - Return-Path, Bounce Address, RFC5321.MailFrom - used during SMTP session",
        "sender": "Indicates who actually submitted the message, differs from From when sending on behalf of another"
    }

    def __init__(self, msg):
        self.from_header = msg.get('from')
        self.return_path = msg.get('return-path')
        self.reply_to = msg.get('reply-to')
        self.sender = msg.get('sender')

    def __str__(self):
        return f"From: {self.from_header}\nReturn-Path: {self.return_path}\nReply-To: {self.reply_to}\nSender: {self.sender}"
    
@dataclass
class SPFResult:
    verdict: str | None = None      # pass / fail / softfail / neutral / none
    comment: str | None = None
    mailfrom: str | None = None
    raw: dict = field(default_factory=dict)

@dataclass
class DKIMResult:
    verdict: str | None = None      # pass / fail / none / neutral / temperror...
    domain: str | None = None       # from header.i or header.d
    selector: str | None = None     # from header.s
    raw: dict = field(default_factory=dict)

@dataclass
class DMARCResult:
    verdict: str | None = None      # pass / fail / none
    from_domain: str | None = None  # from header.from
    policy: str | None = None       # from p= (e.g. 'REJECT')
    raw: dict = field(default_factory=dict)

@dataclass
class AuthenticationInfo:
    spf: SPFResult | None = None
    dkim: list[DKIMResult] = field(default_factory=list)
    dmarc: DMARCResult | None = None
    server: str | None = None
    raw: str = ""

    @classmethod
    def from_header(cls, value: str) -> "AuthenticationInfo":
        spf = None
        dkim = None
        dmarc = None
        server = None

        segments = value.split(';')
        server = segments[0].strip()

        for segment in segments:
            segment = segment.strip()
            if segment.startswith("spf="):
                spf = AuthenticationInfo._parse_spf(segment)

            if segment.startswith("dkim="):
                dkim = AuthenticationInfo._parse_dkim(segment)

            if segment.startswith("dmarc"):
                dmarc = AuthenticationInfo._parse_dmarc(segment)

        return cls(spf=spf, dkim=dkim, dmarc=dmarc, server=server, raw=value)
    
    @classmethod
    def _parse_spf(self, segment):

        match = re.search(re_group_parens, segment)
        comment = match.group(1) if match else None
        cleaned = re.sub(re_group_parens, '', segment)

        results = {}
        for item in cleaned.split():
            if '=' not in item:
                continue
            k, v = item.split('=', 1)
            results[k] = v

        results["comment"] = comment

        return SPFResult(
            verdict=results["spf"],
            mailfrom=results["smtp.mailfrom"],
            comment=results["comment"],
            raw=segment
        )
    
    @classmethod
    def _parse_dkim(self, segment):
        
        result = {}
        for item in segment.split():
            if '=' not in item:
                continue
            k, v = item.split('=', 1)
            result[k] = v

        dkim_domain = None
        if "header.d" in result:
            dkim_domain = result["header.d"]
        elif "header.i" in result:
            dkim_domain = result["header.i"]
        
        return DKIMResult(
            verdict=result["dkim"],
            domain=dkim_domain,
            selector=result["header.s"],
            raw=segment
        )
    
    @classmethod
    def _parse_dmarc(self, segment):
        result = {}
        match = re.search(re_group_parens, segment)
        policy = match.group(1) if match else None
        cleaned = re.sub(re_group_parens, '', segment)

        for item in cleaned.split():
            if '=' not in item:
                continue
            k, v = item.split('=')
            result[k] = v

        result["policy"] = policy

        return DMARCResult(
            verdict=result["dmarc"],
            from_domain=result["header.from"],
            policy=result["policy"],
            raw=segment
        )

@dataclass
class RoutingHop:
    RE_GROUP_BY = r'by\s(.*?)\s'
    RE_GROUP_FROM = r'from\s(.*?)\s'
    RE_GROUP_FOR = r'for\s<(.*?)>'

    by: str | None = None
    frm: str | None = None   # 'from' is a keyword, hence the rename
    for_addr: str | None = None
    timestamp: dt.datetime | None = None
    raw: str = ""
    def __init__(self, hop):
        self.raw = hop
        self.by = self.get_by_host(hop)
        self.frm = self.get_from_host(hop)
        self.for_address = self.get_for_address(hop)
        self.timestamp = self.get_timestamp(hop)

    def get_by_host(self, hop):
        match = re.search(self.RE_GROUP_BY, hop)
        by_host = match.group(1) if match else None
        return by_host
    
    def get_from_host(self, hop):
        match = re.search(self.RE_GROUP_FROM, hop)
        from_host = match.group(1) if match else None
        return from_host
    
    def get_for_address(self, hop):
        match = re.search(self.RE_GROUP_FOR, hop)
        for_address = match.group(1) if match else None
        return for_address
    
    def get_timestamp(self, hop):
        dt_format = '%a, %d %b %Y %H:%M:%S %z'
        t = hop.split(';')[-1].strip()
        t = re.sub(re_group_parens, '', t).strip()
        
        return dt.datetime.strptime(t, dt_format)