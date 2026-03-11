Extract all actionable coding rules from the selected text.
For each rule:
- Convert to imperative statement starting with ALWAYS, NEVER, PREFER, or AVOID
- Remove background, rationale, history, author info
- Preserve code snippets in fenced code blocks with language tags
- Label good examples with "✅ Do this:" and bad with "❌ Not this:"
- Classify each rule under ONE of these headings:
  ## Naming Conventions
  ## Code Style & Formatting
  ## Functions & Methods
  ## Error Handling
  ## Architecture & Patterns
  ## Testing
  ## Security
  ## Dependencies & Imports
  ## Documentation & Comments
  ## Database & Data
  ## API Design
  ## Performance
  ## Git & Version Control
  ## Framework Specific

Format as markdown with ## headings and bullet points.
Output ONLY the rules. No explanations.
If no actionable rules exist in this text, output: (no rules in this section)
