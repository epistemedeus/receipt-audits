"""Parse the requester's captured public ledger without using peer audit totals."""
from html.parser import HTMLParser
import html
import re
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,d):self.parts.append(d)
def plain(s):
    p=Text();p.feed(s);return html.unescape(''.join(p.parts)).strip()
class Item(HTMLParser):
    def __init__(self):super().__init__();self.depth=0;self.active=[];self.fields={}
    def handle_starttag(self,tag,attrs):
        if tag!='span':return
        self.depth+=1
        cls=dict(attrs).get('class','')
        if cls.startswith('fjx-c-'):self.active.append([cls[6:],self.depth,[]])
    def handle_data(self,data):
        for _,_,parts in self.active:parts.append(data)
    def handle_endtag(self,tag):
        if tag!='span':return
        remaining=[]
        for name,depth,parts in self.active:
            if depth==self.depth:self.fields.setdefault(name,[]).append(''.join(parts).strip())
            else:remaining.append([name,depth,parts])
        self.active=remaining;self.depth-=1
def ledger(s):
    entries=[]
    for item in re.findall(r'<li class="fjx-c-item">(.*?)</li>',s,re.S):
        parsed=Item();parsed.feed(item)
        def field(name):
            values=parsed.fields.get(name,[])
            if name=='meta':values=[x for x in values if re.match(r'^\d{4}-\d\d-\d\d · ',x)]
            if len(values)!=1:raise ValueError('missing or ambiguous ledger '+name)
            return values[0]
        hashes=re.findall(r'https://bscscan.com/tx/(0x[0-9a-fA-F]{64})',item)
        if len(hashes)!=1:raise ValueError('ledger entry lacks unique receipt')
        meta=field('meta');date=meta[:10];label=meta[13:].split(' · ')[0]
        rawamount=field('amt')
        amount=rawamount.split(' FLAPJAX',1)[0].replace(',','')
        if not re.fullmatch(r'\d+(\.\d{1,18})?',amount):raise ValueError('invalid ledger amount')
        whole,_,frac=amount.partition('.')
        entries.append({'tx':hashes[0].lower(),'date':date,'label':label,'work':field('work'),'displayAmount':rawamount,'atoms':str(int(whole)*10**18+int(frac.ljust(18,'0') or 0))})
    if not entries:raise ValueError('missing public ledger')
    return entries
