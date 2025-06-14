# Possible Vulnerabilities Investigation

## File Upload Endpoints

From the gobuster results in `Lists url.txt`, the following endpoints were found:

- **`/upload`** (Status: 200) — Likely processes file uploads
- **`/download`** (Status: 200) — Handles file downloads

---

## Potential Vulnerable Endpoints to Test

### 1. File Upload Vulnerabilities

- **Target:** `/upload` endpoint
- **Method:** Try uploading malicious files disguised as Excel files
- **Techniques to try:**
  - Rename `.php` files to `.xlsx`
  - Double extension attacks (e.g., `malicious.php.xlsx`)
  - Null byte injection (`malicious.php%00.xlsx`)
  - MIME type manipulation

### 2. File Download Vulnerabilities

- **Target:** `/download` endpoint
- **Method:** Path traversal attacks
- **Test parameters:**
  - `fileName=../../../etc/passwd`
  - `fileName=..\..\..\..\windows\system32\drivers\etc\hosts`
  - `fileName=../config/database.properties`

### 3. CRUD Operation Endpoints (RuoYi Framework Patterns)

- `/system/user/list` — User management
- `/system/role/list` — Role management
- `/system/menu/list` — Menu management
- `/system/dept/list` — Department management

### 4. Admin Panel Access

- `/index` — Main dashboard (mentioned in `login.js`)
- `/system` — System management section
- `/monitor` — Monitoring section
- `/tool` — Tools section

### 5. API Endpoints to Test

- `/login` — Login processing
- `/register` — Registration processing
- `/captcha/captchaImage` — CAPTCHA generation
- `/common/download` — File download handler

---

## Specific Vulnerability Tests

### File Upload Bypass Techniques

- **Extension manipulation:** Upload `.jsp`, `.jspx`, or `.php` files renamed as `.xlsx`
- **Content-Type spoofing:** Change MIME type to `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Polyglot files:** Create files that are both valid Excel and executable code

### Parameter Injection Tests

Test these parameters in various endpoints:

- `id=1' OR '1'='1` (SQL injection)
- `id=../../../etc/passwd` (Path traversal)
- `id=<script>alert('xss')</script>` (XSS)

### Authentication Bypass

- Try accessing admin URLs directly without authentication
- Test for default credentials (`admin/admin`, `admin/123456`, etc.)
- Look for session fixation vulnerabilities

### Information Disclosure

- Check for exposed configuration files
- Look for database backup files
- Test for directory listing on `/upload`, `/download`, `/temp`

---

## Tools You Could Use

- **Burp Suite** — Intercepting and modifying requests
- **OWASP ZAP** — Automated vulnerability scanning
- **SQLMap** — SQL injection testing
- **Gobuster/Dirb** — Additional directory enumeration
