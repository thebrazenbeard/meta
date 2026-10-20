# Method-choice and input commitment protocol (experimental)

This module separates *choosing* one prewritten method, *executing* that local method on a frozen challenge, and *comparing submitted outputs with labels supplied later*. It does not discover new methods or install a new cognitive architecture.

```python
from dataclasses import asdict
from meta.core import freeze
from meta.experiment import commit_method, run_committed, adjudicate

challenge = [("case-a", 2), ("case-b", 3)]
commitment = commit_method("trial-001", freeze("parity"), challenge)
print(asdict(commitment))  # Have an independent curator retain this record.
predictions = run_committed(commitment, challenge)  # No labels supplied here.
# A later, separate evaluation phase supplies previously withheld truth labels:
result = adjudicate(commitment, challenge, predictions,
                    {"case-a": 0, "case-b": 1})
print(result)
```

The commitment binds a challenge identifier, frozen local method identity and sorted challenge inputs. Changing the selected method, source digest, challenge, or any case input fails. `adjudicate` rejects missing/extra case IDs, malformed labels, and submitted results that disagree with this known prewritten method's results. The output records method/label digests and observed toy accuracy.

**Adversarial limit:** an attacker can compute the prewritten method's answers without ever invoking the claimed worker; output agreement is not execution provenance. A method's local source digest does not measure mutable dependency closure, environment, upstream sources, or a later external consumer. The same caller can rewrite commitment and results unless an independent curator keeps the original. SHA digests alone provide no timestamp, data secrecy, isolated evaluator, or blind outcome custody.

Only an external test runner with separate label ownership, concrete held-out tasks, process/permission isolation and witnessed invocation can raise those claims. The returned fields explicitly keep independence and autonomous method discovery `False`.
