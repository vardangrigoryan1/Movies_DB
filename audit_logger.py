import json
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, log_path="project/data/audit/audit_log.json"):
        self.log_path = os.path.abspath(log_path)
        
        #creating the file if it does not exist
        with open(self.log_path, 'a'):
            pass

    def _read_logs(self):
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return []

        with open(self.log_path, 'r') as f:
            content = f.read()
        return json.loads(f'[{content}]')


    def _write_logs(self, all_entries):
        with open(self.log_path, 'w') as f:
            for i, entry in enumerate(all_entries):
                json.dump(entry, f, indent=4)
                if i < len(all_entries) - 1:
                    f.write(',\n')
            f.write('\n')


    def _log_entry(self, entry):
        entry["timestamp"] = datetime.now().isoformat()
        
        all_entries = self._read_logs()
        all_entries.append(entry)
        self._write_logs(all_entries)

    def log_insertion(self, movie_id, movie_title):
        entry = {
            "action": "INSERTED",
            "movie_id": movie_id,
            "title": movie_title,
        }
        self._log_entry(entry)

    def log_deletion(self, movie_id, movie_title):
        entry = {
            "action": "REMOVED",
            "movie_id": movie_id,
            "title": movie_title,
        }
        self._log_entry(entry)

    def log_modification(self, movie_id, movie_title, changes):
        entry = {
            "action": "MODIFIED",
            "movie_id": movie_id,
            "title": movie_title,
            "modifications": changes
        }
        self._log_entry(entry)

#©Vardan Grigoryan