import json
from app.infrastructure.ssh_client import SSHClientAdapter

class RuleService:
    def __init__(self, ssh_client: SSHClientAdapter):
        self.ssh_client = ssh_client
        self.rule_file = "/var/lib/suricata/rules/custom.rules"

    def get_rules(self, ip: str):
        # Создаем файл если его нет, затем читаем
        cmd = f"mkdir -p /var/lib/suricata/rules && touch {self.rule_file} && cat {self.rule_file} | grep -v '^$' || true"
        try:
            raw = self.ssh_client.execute(ip, cmd)
            if not raw: return []
            return [{"id": idx, "rule_text": line} for idx, line in enumerate(raw.split('\n'))]
        except Exception:
            return []

    def add_rule(self, ip: str, rule_text: str):
        safe_rule = rule_text.replace("'", "'\\''")
        # Добавляем правило и игнорируем ошибку suricatasc, если демон выключен или завис
        cmd = f"mkdir -p /var/lib/suricata/rules && echo '{safe_rule}' >> {self.rule_file} && (timeout 2 suricatasc -c reload-rules || echo '{{\"message\": \"done\", \"return\": \"OK (daemon off)\"}}')"
        raw_result = self.ssh_client.execute(ip, cmd)
        try: return json.loads(raw_result)
        except: return raw_result

    def delete_rule(self, ip: str, rule_text: str):
        safe_rule = rule_text.replace("'", "'\\''")
        # Скобки и || true важны: если это последнее правило, grep вернет код 1, но мы все равно должны переместить пустой файл
        cmd = f"(grep -F -v -x '{safe_rule}' {self.rule_file} > /tmp/cr.tmp || true) && mv /tmp/cr.tmp {self.rule_file} && (timeout 2 suricatasc -c reload-rules || echo '{{\"message\": \"done\"}}')"
        raw_result = self.ssh_client.execute(ip, cmd)
        try: return json.loads(raw_result)
        except: return raw_result

    def sync_rules_from_source(self, ip: str, repo_rules: list):
        # 1. Получаем существующие правила с сенсора
        existing_rules_data = self.get_rules(ip)
        existing_rules = [r['rule_text'].strip() for r in existing_rules_data]
        existing_set = set(existing_rules)
        
        # 2. Фильтруем дубликаты
        new_rules_added = 0
        updated_rules = list(existing_rules)
        for rule in repo_rules:
            rule_clean = rule.strip()
            if not rule_clean:
                continue
            if rule_clean not in existing_set:
                updated_rules.append(rule_clean)
                existing_set.add(rule_clean)
                new_rules_added += 1
                
        if new_rules_added == 0:
            return {
                "status": "success", 
                "message": "Все правила из источника уже присутствуют на сенсоре (дубликаты пропущены)", 
                "added_count": 0
            }
            
        # 3. Записываем обратно на сенсор через sftp-загрузку временного файла
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rules', delete=False, encoding='utf-8') as f:
            f.write('\n'.join(updated_rules) + '\n')
            temp_local_path = f.name
            
        try:
            remote_temp_path = "/tmp/custom.rules.tmp"
            self.ssh_client.upload_file(ip, temp_local_path, remote_temp_path)
            
            cmd = f"mkdir -p /var/lib/suricata/rules && mv {remote_temp_path} {self.rule_file} && (timeout 2 suricatasc -c reload-rules || echo '{{\"message\": \"done\", \"return\": \"OK (daemon off)\"}}')"
            raw_result = self.ssh_client.execute(ip, cmd)
            return {
                "status": "success", 
                "message": f"Правила успешно обновлены. Добавлено новых правил: {new_rules_added}.", 
                "added_count": new_rules_added, 
                "reload_result": raw_result
            }
        finally:
            if os.path.exists(temp_local_path):
                os.remove(temp_local_path)

    def batch_delete_rules(self, ip: str, rule_texts: list):
        # 1. Получаем текущие правила с сенсора
        existing_rules_data = self.get_rules(ip)
        existing_rules = [r['rule_text'].strip() for r in existing_rules_data]
        
        # 2. Фильтруем удаляемые правила
        delete_set = set(r.strip() for r in rule_texts)
        updated_rules = [r for r in existing_rules if r not in delete_set]
        
        # 3. Записываем обновленный список правил обратно через SFTP
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rules', delete=False, encoding='utf-8') as f:
            f.write('\n'.join(updated_rules) + '\n')
            temp_local_path = f.name
            
        try:
            remote_temp_path = "/tmp/custom.rules.tmp"
            self.ssh_client.upload_file(ip, temp_local_path, remote_temp_path)
            
            cmd = f"mkdir -p /var/lib/suricata/rules && mv {remote_temp_path} {self.rule_file} && (timeout 2 suricatasc -c reload-rules || echo '{{\"message\": \"done\", \"return\": \"OK (daemon off)\"}}')"
            raw_result = self.ssh_client.execute(ip, cmd)
            return {
                "status": "success", 
                "message": f"Правила успешно удалены ({len(rule_texts)} шт.)", 
                "reload_result": raw_result
            }
        finally:
            if os.path.exists(temp_local_path):
                os.remove(temp_local_path)
