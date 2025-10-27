import email
IMAP_HOST = 'imap.gmail.com'
EMAIL_ADDR = os.environ['GMAIL_ADDRESS']
APP_PASS = os.environ['GMAIL_APP_PASSWORD']
LABEL = os.environ.get('GMAIL_IMAP_LABEL', 'PhotosToSite')
OUTDIR = os.environ.get('OUTDIR', 'images')
ALLOWED = {'.jpg','.jpeg','.png','.gif','.webp','.avif'}


os.makedirs(OUTDIR, exist_ok=True)


conn = imaplib.IMAP4_SSL(IMAP_HOST)
try:
conn.login(EMAIL_ADDR, APP_PASS)
except imaplib.IMAP4.error as e:
print('Login failed:', e)
sys.exit(2)


# Select label
status, _ = conn.select(f'"{LABEL}"', readonly=False)
if status != 'OK':
print('Could not select label. Does it exist? Label:', LABEL)
sys.exit(3)


# Search for UNSEEN messages
status, data = conn.search(None, 'UNSEEN')
if status != 'OK':
print('Search failed')
sys.exit(4)


ids = data[0].split()
print(f'Found {len(ids)} unseen message(s) in label {LABEL}')


safe = lambda s: re.sub(r'[^A-Za-z0-9_.-]+', '_', s)


saved_any = False
for mid in ids:
status, msgdata = conn.fetch(mid, '(RFC822)')
if status != 'OK':
continue
msg = email.message_from_bytes(msgdata[0][1])
subj = msg.get('Subject','(no subject)')
date_hdr = msg.get('Date')
dt = datetime.utcnow().strftime('%Y%m%d_%H%M%S')


# Traverse parts
for part in msg.walk():
if part.get_content_maintype() == 'multipart':
continue
filename = part.get_filename()
ctype = part.get_content_type() or ''
if not filename:
# Skip inline text parts
if not ctype.startswith('image/'):
continue
# Synthesize a name for inline images
ext = {
'image/jpeg':'.jpg', 'image/png':'.png', 'image/gif':'.gif',
'image/webp':'.webp', 'image/avif':'.avif'
}.get(ctype, '')
filename = f'inline_{dt}{ext}'
ext = os.path.splitext(filename)[1].lower()
if ext not in ALLOWED:
continue
base = safe(os.path.splitext(os.path.basename(filename))[0])
outname = f"{dt}_{base}{ext}"
path = os.path.join(OUTDIR, outname)
with open(path, 'wb') as f:
f.write(part.get_payload(decode=True))
print('Saved', path, 'from', subj)
saved_any = True


# Mark message as SEEN and add a custom processed label
try:
conn.store(mid, '+X-GM-LABELS', 'ProcessedBySlideshow')
conn.store(mid, '+FLAGS', '\\Seen')
except Exception:
pass


conn.close()
conn.logout()


# Exit code signals whether anything changed
sys.exit(0 if saved_any else 0)
