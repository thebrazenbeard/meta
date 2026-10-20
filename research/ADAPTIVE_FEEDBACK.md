# Monitoring and control: feedback-based method selection

`FeedbackController` selects one of the existing, developer-authored `METHODS` before receiving a label. After a subsequent externally supplied outcome, it scores the selected and other available prewritten methods against that outcome. Rolling loss changes *future choice of method*. This is a **full-information online expert-selection toy**, not new-method invention, spontaneous goal setting, recursive meta-learning or independent knowledge of truth.

The tests show that a fixed parity method can perform well before a rule reversal but fail afterward; the controller changes toward the prewritten inverted-parity option once enough reversed outcomes have been received. This is a useful minimal *monitor -> control* experiment. The rule for changing strategies is itself fixed and has not been improved or discovered by the controller.

## Experimental discipline
- Freeze candidate algorithms and feedback policy, announce distribution-shift generation and score against a frozen method and randomized choice.
- Generate feedback only **after** a method choice and its prediction. Reject replay and mismatched case IDs.
- Distinguish training inputs from purported held-out inputs; `toy_arms` and `domain_shift_probe` reject overlap.
- Score errors before and after the shift separately and compare adaptation latency. Disclose that full-information evaluation of every prewritten method is available after each revealed outcome.
- Independently held labels and a witnessed candidate execution process are necessary for credible qualification. This package does not provide those.
- Investigate whether adaptive selection generalizes to methods with costs, partial feedback, noisy labels and genuinely unseen task families; also include a control with unchanged policy and merely narrated reflection.

Background: Nelson & Narens monitoring/control framework (1990, https://doi.org/10.1016/S0079-7421(08)60053-5), online expert-advice algorithms (Cesa-Bianchi & Orabona, 2021, https://doi.org/10.1146/annurev-statistics-040620-035329).
