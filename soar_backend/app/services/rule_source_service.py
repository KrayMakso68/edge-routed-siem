import subprocess
import tempfile
import os
from app.core.config import settings
from app.infrastructure.database import get_db_connection
from app.domain.schemas import RuleSourceCreate, RuleSourceUpdate

class RuleSourceService:
    def get_all(self):
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM rule_sources").fetchall()
        conn.close()
        return [dict(ix) for ix in rows]

    def get_by_id(self, source_id: int):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM rule_sources WHERE id = ?", (source_id,)).fetchone()
        conn.close()
        if not row:
            raise Exception("Источник правил не найден в БД")
        return dict(row)

    def create(self, dto: RuleSourceCreate):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rule_sources (name, url, branch, rules_path, description) VALUES (?, ?, ?, ?, ?)",
                       (dto.name, dto.url, dto.branch or 'main', dto.rules_path or '', dto.description or ''))
        conn.commit()
        source_id = cursor.lastrowid
        conn.close()
        return self.get_by_id(source_id)

    def update(self, source_id: int, dto: RuleSourceUpdate):
        current = self.get_by_id(source_id)
        name = dto.name if dto.name is not None else current['name']
        url = dto.url if dto.url is not None else current['url']
        branch = dto.branch if dto.branch is not None else current['branch']
        rules_path = dto.rules_path if dto.rules_path is not None else current['rules_path']
        description = dto.description if dto.description is not None else current['description']
        
        conn = get_db_connection()
        conn.execute("UPDATE rule_sources SET name=?, url=?, branch=?, rules_path=?, description=? WHERE id=?",
                     (name, url, branch, rules_path, description, source_id))
        conn.commit()
        conn.close()
        return self.get_by_id(source_id)

    def delete(self, source_id: int):
        conn = get_db_connection()
        conn.execute("DELETE FROM rule_sources WHERE id = ?", (source_id,))
        conn.commit()
        conn.close()

    def fetch_rules_from_git(self, repo_url: str, branch: str = "main", rules_path: str = None) -> list[str]:
        # Clones git repo and gets rules
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = ["git", "clone", "--depth", "1", "-b", branch, repo_url, tmpdir]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    cmd_fallback = ["git", "clone", "--depth", "1", repo_url, tmpdir]
                    result_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True)
                    if result_fallback.returncode != 0:
                        raise Exception(f"Failed to clone: {result_fallback.stderr or result_fallback.stdout}")
                
                rules = []
                if rules_path:
                    full_path = os.path.join(tmpdir, rules_path)
                    if os.path.isfile(full_path):
                        rules.extend(self._read_rules_from_file(full_path))
                    else:
                        raise Exception(f"Rules file not found at path: {rules_path}")
                else:
                    found_any = False
                    for root, dirs, files in os.walk(tmpdir):
                        for file in files:
                            if file.endswith(".rules") or file in ("rules.rules", "custom.rules"):
                                full_path = os.path.join(root, file)
                                rules.extend(self._read_rules_from_file(full_path))
                                found_any = True
                    if not found_any:
                        raise Exception("No rule files found in repository")
                return rules
        except Exception as e:
            if settings.DEMO_MODE:
                return self._get_demo_curated_rules()
            raise e

    def _get_demo_curated_rules(self) -> list[str]:
        return [
            'alert tcp any any -> $HOME_NET 22 (msg:"ET SCAN Potential SSH Brute Force"; flags:S; threshold:type both, track by_src, count 5, seconds 60; sid:2001219; rev:1;)',
            'alert http any any -> $HOME_NET any (msg:"ET WEB_SERVER Possible SQL Injection Attempt (UNION SELECT)"; content:"UNION"; nocase; content:"SELECT"; nocase; sid:2000001; rev:2;)',
            'alert tcp any any -> $HOME_NET [80,443] (msg:"ET ATTACK_RESPONSE Metasploit Meterpreter Reverse HTTPS Certificate"; content:"|16 03 01|"; sid:2020001; rev:1;)',
            'alert dns any any -> any any (msg:"ET DNS Query for Suspicious TLD (.top)"; dns.query; content:".top"; endswith; sid:2025110; rev:1;)',
            'alert icmp any any -> $HOME_NET any (msg:"ET SCAN Suspicious ICMP Ping Sweep"; itype:8; threshold:type both, track by_src, count 20, seconds 10; sid:2100342; rev:1;)',
            'alert tcp any any -> $HOME_NET 445 (msg:"ET EXPLOIT Possible EternalBlue SMB MS17-010 Probe"; flow:to_server,established; content:"|ff|SMB|72|"; offset:4; depth:5; sid:2024218; rev:3;)',
            'alert http any any -> $HOME_NET any (msg:"ET WEB_SERVER Log4j RCE Attempt (CVE-2021-44228)"; content:"${jndi:"; nocase; sid:2034647; rev:1;)'
        ]

    def _read_rules_from_file(self, filepath: str) -> list[str]:
        rules = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    rules.append(line)
        return rules
