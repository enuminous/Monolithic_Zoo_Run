# Limitations

- HUMMINGBIRD can enforce only conditions encoded in the frozen specification.
- A valid hash chain detects edits within the available log; without external anchoring it cannot prove that a complete alternate log was never substituted.
- Distribution-shift scores and compute measurements must come from trustworthy instrumentation.
- Information parity by feature name does not prove semantic parity, preprocessing parity, freshness, or data quality.
- A human may honestly record an intervention incompletely.
- A local monitor is not independent merely because it runs in another process. Serious tests require separate permissions, read-only telemetry, frozen code, and independent custody of evidence.
- State thresholds can themselves be misspecified or gamed.
- GREEN means encoded conformance, not scientific truth.
- RED means a registered breach, not candidate failure.
- BLACK means the registered question is uninterpretable from the surviving evidence.
- The included benchmark uses synthetic, known faults and cannot establish performance in a commercial or safety-critical pilot.
- This software has not been validated for medical, financial, legal, safety-critical, or autonomous decisions.
