
import json
import hashlib
import time
from typing import Dict, Any

class EthosAuditLogger:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.audit_log = [] # Mock immutable store (e.g., TrustLedger/blockchain)

    def _create_log_entry(self, input_data: Dict[str, Any], prediction: Any, user_group: str) -> Dict[str, Any]:
        """Creates a standardized, time-stamped log entry."""
        log_entry = {
            "timestamp": int(time.time() * 1000),
            "model_id": self.model_id,
            "input_data": input_data,
            "prediction_output": prediction,
            "sensitive_group": user_group, # Key fairness metric identifier
            "hash": "" # Placeholder for the final cryptographic hash
        }
        return log_entry

    def _generate_verifiable_hash(self, entry: Dict[str, Any]) -> str:
        """Generates a cryptographic hash for the log entry's content."""
        # Use canonicalized JSON string to ensure deterministic hashing
        canonical_string = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()

    def log_prediction(self, input_data: Dict[str, Any], prediction: Any, user_group: str):
        """
        Main logging function: creates entry, calculates hash, and saves to the immutable log.
        """
        entry = self._create_log_entry(input_data, prediction, user_group)
        # 1. The integrity check (hash) is applied *to* the data
        entry["hash"] = self._generate_verifiable_hash(entry)
        
        # 2. Add to the immutable audit log
        self.audit_log.append(entry)
        
        # 3. In a real system, this would be asynchronously written to TrustLedger (Solution #6)
        print(f"[EthosGuard] Logged prediction for group '{user_group}'. Hash: {entry['hash'][:10]}...")

    def run_drift_check(self, historical_logs: List[Dict[str, Any]] = None):
        """
        MOCK: Simulates running a drift check by validating all stored hashes 
        and analyzing prediction distribution.
        """
        logs = historical_logs if historical_logs is not None else self.audit_log
        
        # 1. Hash Integrity Check (Ensures no tampering)
        for entry in logs:
            stored_hash = entry["hash"]
            # Clear the hash before re-calculation to verify the original payload
            entry_copy = entry.copy()
            entry_copy["hash"] = "" 
            re_calculated_hash = self._generate_verifiable_hash(entry_copy)
            
            if stored_hash != re_calculated_hash:
                print(f"🚨 INTEGRITY FAILURE: Log entry hash mismatch detected!")
                return False
        
        # 2. Bias/Drift Analysis (Simple example: check group prediction distribution)
        prediction_counts = {}
        for entry in logs:
            group = entry["sensitive_group"]
            prediction = entry["prediction_output"]
            
            if group not in prediction_counts:
                prediction_counts[group] = {}
            
            pred_key = str(prediction)
            prediction_counts[group][pred_key] = prediction_counts[group].get(pred_key, 0) + 1

        print("\n[EthosGuard] Bias/Drift Summary (Simple Prediction Count):")
        for group, counts in prediction_counts.items():
             print(f"  Group '{group}': {counts}")

        # In a real system, a statistical test would determine if distributions differ significantly

# --- Demonstration ---

logger = EthosAuditLogger(model_id="CreditScoreV1")

# Simulate predictions for two different (sensitive) user groups
logger.log_prediction({"age": 30, "income": 60000}, prediction=1, user_group="A") # Approved
logger.log_prediction({"age": 55, "income": 120000}, prediction=1, user_group="B") # Approved
logger.log_prediction({"age": 22, "income": 35000}, prediction=0, user_group="A") # Denied
logger.log_prediction({"age": 40, "income": 40000}, prediction=0, user_group="B") # Denied
logger.log_prediction({"age": 33, "income": 45000}, prediction=1, user_group="B") # Approved

logger.run_drift_check()
      
