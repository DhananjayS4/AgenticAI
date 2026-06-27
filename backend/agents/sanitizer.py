import re

class SanitizerAgent:
    def __init__(self):
        # Regex patterns for common sensitive information
        self.patterns = {
            "EMAIL": r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            "PHONE": r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
            "CREDIT_CARD": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "API_KEY": r'\b(?:key|password|secret|pwd|token)\s*[:=]\s*[\'"][a-zA-Z0-9_\-\.\@\!]{4,}[\'"]\b',
        }
        self.logs = []

    def sanitize(self, text: str) -> tuple[str, dict]:
        """
        Scan text for sensitive data, redact it, and return the sanitized text 
        along with a mapping dict to restore it later.
        """
        mapping = {}
        sanitized_text = text
        
        for name, pattern in self.patterns.items():
            matches = list(set(re.findall(pattern, sanitized_text)))
            for i, match in enumerate(matches):
                # For API key, we extract the sensitive value to encrypt/redact, keeping the key name
                if name == "API_KEY":
                    # Parse the actual secret value
                    parts = re.split(r'[:=]', match)
                    key_part = parts[0].strip()
                    val_part = parts[1].strip().strip('\'"')
                    
                    placeholder = f"[REDACTED_{name}_{i+1}]"
                    mapping[placeholder] = val_part
                    
                    # Reconstruct the string without the secret
                    replacement = f"{key_part} = {placeholder}"
                    sanitized_text = sanitized_text.replace(match, replacement)
                    self.logs.append(f"Security Alert: Redacted credential in expression: '{key_part} = ...'")
                else:
                    placeholder = f"[REDACTED_{name}_{i+1}]"
                    mapping[placeholder] = match
                    sanitized_text = sanitized_text.replace(match, placeholder)
                    suffix = match[-3:] if len(match) > 6 else ""
                    self.logs.append(f"Security Alert: Redacted sensitive {name.lower()} '{match[:3]}...{suffix}' to {placeholder}")
        
        return sanitized_text, mapping

    def desanitize(self, text: str, mapping: dict) -> str:
        """Restore redacted placeholders with original values."""
        restored_text = text
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text

    def get_logs(self):
        """Return the security logs generated during sanitization."""
        return self.logs

    def clear_logs(self):
        self.logs = []
