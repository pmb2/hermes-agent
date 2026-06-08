# Phase 5: Paper Drafting

> Extracted from `skills/research/research-paper-writing/SKILL.md` as a reference.
> Referenced from the main skill file to keep it under the 100KB size limit.

**Goal**: Write a complete, publication-ready paper.

### Context Management for Large Projects

A paper project with 50+ experiment files, multiple result directories, and extensive literature notes can easily exceed the agent's context window. Manage this proactively:

**What to load into context per drafting task:**

| Drafting Task | Load Into Context | Do NOT Load |
|---------------|------------------|-------------|
| Writing Introduction | `experiment_log.md`, contribution statement, 5-10 most relevant paper abstracts | Raw result JSONs, full experiment scripts, all literature notes |
| Writing Methods | Experiment configs, pseudocode, architecture description | Raw logs, results from other experiments |
| Writing Results | `experiment_log.md`, result summary tables, figure list | Full analysis scripts, intermediate data |
| Writing Related Work | Organized citation notes (Step 1.4 output), .bib file | Experiment files, raw PDFs |
| Revision pass | Full paper draft, specific reviewer concerns | Everything else |

**Principles:**
- **`experiment_log.md` is the primary context bridge** — it summarizes everything needed for writing without loading raw data files (see Step 4.6)
- **Load one section's context at a time** when delegating. A sub-agent drafting Methods doesn't need the literature review notes.
- **Summarize, don't include raw files.** For a 200-line result JSON, load a 10-line summary table. For a 50-page related paper, load the 5-sentence abstract + your 2-line note about its relevance.
- **For very large projects**: Create a `context/` directory with pre-compressed summaries:
  ```
  context/
  └── introduction/            # Context bundles per section
      ├── context.md           # ~500 word summary of claims + key results
      └── seed_papers.txt      # 10 most relevant paper abstracts
  ```

### Step 5.1: Write the Introduction

**Purpose**: Hook the reader → motivate the problem → state the gap → present your contribution → outline the paper.

**Structure** (5-paragraph model, ~1 page):

| Paragraph | Purpose | Content |
|-----------|---------|---------|
| 1: Hook | Motivate the problem | Start with a concrete, relatable problem — not "in recent years". 2-3 sentences. |
| 2: Existing work | What has been done | Brief summary of relevant approaches. 2-3 sentences. |
| 3: Gap | What's missing | The specific limitation you address. 1-2 sentences. |
| 4: This paper | Your contribution + key insight | What you did and why it works. 3-5 sentences. |
| 5: Outline | Roadmap | "In Section 2, we formalize...". 1-2 sentences. |

**Example** (from a real NeurIPS paper):

> Humans learn from both demonstration and high-level instructions. While imitation learning has made great progress in learning from demonstrations, reward specification remains a bottleneck for learning from instructions. Existing approaches require manual reward engineering, which is time-consuming and prone to misspecification. In this work, we propose an automatic method for learning reward functions from natural language instructions. Our approach leverages a pretrained language model to parse instructions into reward features, enabling zero-shot generalization to new tasks. We evaluate our method on a suite of robotic manipulation tasks and find that it outperforms both hand-crafted rewards and learned reward baselines.

**Common pitfalls:**
- **Too vague**: "In recent years, deep learning has achieved great success..." (delete — not specific)
- **No gap**: Describes what's been done but not what's missing
- **Contribution list instead of narrative**: "Our contributions are: (1)... (2)..." as a list in the intro (save for end of intro as 1-2 sentences max)
- **Too long**: The intro should be 8-15 sentences. If longer, you're writing a survey, not a paper.
- **Too short**: 3-4 sentences that just say "we did X" — set up the landscape first.

### Step 5.2: Write Related Work

**Purpose**: Position your work in the existing landscape. Show you understand the field and why your approach is different.

**Structure:**
- Group related work thematically (not chronologically)
- 2-4 paragraphs, placed after introduction (NeurIPS/ICML) or before conclusion (some venues)
- Each paragraph: "Many approaches have been proposed for X. Method A does [summary], but [limitation]. Method B does [summary], but [limitation]. Our approach addresses these by [your key insight]."

**Keep it fair:**
- Do NOT misrepresent baselines (reviewers will catch this)
- Do NOT bury strong baselines in a single sentence while describing your method in a paragraph
- If a specific baseline is the closest competitor, give it a dedicated paragraph
- If citing concurrent work, note "independent and concurrent" — it's common and acceptable

**Breadth vs depth tradeoff:**
- Too broad → reads like a literature survey, not a paper (limit to 15-25 citations)
- Too narrow → looks like you don't understand the context (include adjacent sub-fields)
- Rule of thumb: cover the immediate sub-field well, mention adjacent areas in 1-2 sentences

### Step 5.3: Write the Method Section

**Structure**: Problem setup → Notation → Method description → Key insight.

```latex
\section{Method}
\label{sec:method}

\subsection{Problem Setup}
% Formal definition of the problem
Let $\mathcal{X}$ be the input space and $\mathcal{Y}$ the output space...

\subsection{Our Approach}
% Core method description with clear notation
We propose a novel architecture consisting of three components...
[Continue with sub-sections as needed]

\subsection{Key Theoretical Insight}
% Why it works — the most important paragraph in the paper
The key insight is that...
```

**Rules:**
1. **Self-contained**: Reader should understand the method without reading other papers
2. **Notation matters**: Keep it consistent, define everything, avoid ambiguity
3. **Reproducibility**: Include all details needed to reproduce (architecture specifics, hyperparameters, training details)
4. **One figure**: A method diagram helps enormously — use TikZ (see below)
5. **Pseudocode**: For complex algorithms, use `algorithm2e` (not pseudocode in plain text)
6. **Don't bury the lead**: The key insight should be in the first paragraph of the method section, not hidden on page 3

### Step 5.4: Write the Experiments Section

**Structure**: Setup → Main results → Ablations → Analysis.

```latex
\section{Experiments}
\label{sec:experiments}

\subsection{Experimental Setup}
% Datasets, baselines, metrics, hyperparameters, compute

\subsection{Main Results}
% Comparison against baselines (Table 1)
% Highlight your method's performance

\subsection{Ablation Studies}
% Does each component matter? (Table 2)

\subsection{Analysis}
% Additional insights, scaling behavior, qualitative results
```

**Rules:**
1. **Every claim is backed by a result.** If you say "our method outperforms X," there must be a table showing it.
2. **Baselines must be strong.** Use the latest, best-tuned baselines. Weak baselines are the #1 reason for rejection.
3. **Statistical significance.** Report mean ± std over 3-5 random seeds. Use statistical tests (t-test, bootstrap) when comparing.
4. **Compute budget.** Report training time, GPU hours, and hardware.
5. **Error bars on all plots.** No error bars = immediately suspicious.
6. **Ablations must be informative.** "Without component X" means removing X, not setting a hyperparameter to 0.
7. **Hyperparameters.** Report chosen values and how they were selected. A brief hyperparameter sensitivity analysis shows rigor.

### Step 5.5: Write the Conclusion

**Structure**: Summary → Limitations → Future work → Broader impact (if separate section).

```
- Restate the problem and your contribution (1-2 sentences)
- Summarize key findings (1-2 sentences)
- List limitations honestly (1-2 sentences) — reviewers appreciate this
- Suggest future work (1 sentence max, don't propose 5 future directions)
- Broader impact (if required, usually a separate section)
```

**Pitfalls:**
- Don't introduce new results or citations
- Don't re-state the entire abstract
- Don't claim "first" or "novel" — let the work speak
- Limitations are not weaknesses — honest limitations build trust

### Step 5.6: Write the Abstract

**Last**, after the paper body is complete. The abstract is the most-read part and must distill the entire paper into 150-250 words.

**Structure** (4-6 sentences):
1. **Problem** (1 sentence): What is the problem and why does it matter?
2. **Gap** (1 sentence): What's missing from existing work?
3. **Method** (1-2 sentences): What did you do?
4. **Results** (1 sentence): Key quantitative findings — include numbers.
5. **Significance** (1 sentence): Why should the community care?

**Example** (same paper as intro example):

> Learning robotic skills from human instructions requires mapping language to reward functions. Existing methods rely on manually engineered reward templates, which limit generalization to new tasks. We propose Language-to-Reward (L2R), a method that uses a pretrained language model to automatically parse natural language instructions into dense reward features. L2R outperforms both hand-crafted rewards and learned reward baselines across 12 manipulation tasks, achieving 23% higher success rates while requiring no task-specific engineering. Our results demonstrate that language models can serve as effective prior for reward specification, enabling generalization to unseen tasks without additional training data.

**Rules:**
- Includes numbers (quantitative claims, not qualitative)
- No citations (abstracts cite sparingly if at all)
- No abbreviations without definition
- Must stand alone (reader should understand without reading the paper)
- Write in active voice

### Step 5.7: Write the Title

The title is the **first thing** reviewers and readers see. It alone determines click-through rate on arXiv.

**Good title patterns:**
- **Claim-based**: "[Method]: [Key Property] using [Technique]" — e.g., "Decision Transformer: Reinforcement Learning via Sequence Modeling"
- **Question-based**: "Can [Technique] Solve [Problem]?" — e.g., "Can Wikipedia Help Offline Reinforcement Learning?"
- **Insight-based**: "[Property] is All You Need" — use sparingly

**Rules:**
- 10-15 words max
- No acronyms without expansion
- No puns or wordplay (they don't translate)
- Should still make sense if the paper never existed
- Avoid colon if possible; if needed, only one colon

**Check against confusion matrix:**
1. Does it describe the method?
2. Does it describe the problem?
3. Could it describe another paper? (If yes, too generic)

### Step 5.8: Broader Impact / Ethics Statement

Most venues now require or strongly encourage an ethics/broader impact statement. This is not boilerplate — reviewers read it and can flag ethics concerns that trigger desk rejection.

**What to include:**

| Component | Content | Required By |
|-----------|---------|-------------|
| **Positive societal impact** | How your work benefits society | NeurIPS, ICML |
| **Potential negative impact** | Misuse risks, dual-use concerns, failure modes | NeurIPS, ICML |
| **Fairness & bias** | Does your method/data have known biases? | All venues (implicitly) |
| **Environmental impact** | Compute carbon footprint for large-scale training | ICML, increasingly NeurIPS |
| **Privacy** | Does your work use or enable processing of personal data? | ACL, NeurIPS |
| **LLM disclosure** | Was AI used in writing or experiments? | ICLR (mandatory), ACL |

**Writing the statement:**

```latex
\section*{Broader Impact Statement}
% NeurIPS/ICML: after conclusion, does not count toward page limit

% 1. Positive applications (1-2 sentences)
This work enables [specific application] which may benefit [specific group].

% 2. Risks and mitigations (1-3 sentences, be specific)
[Method/model] could potentially be misused for [specific risk]. We mitigate
this by [specific mitigation, e.g., releasing only model weights above size X,
including safety filters, documenting failure modes].

% 3. Limitations of impact claims (1 sentence)
Our evaluation is limited to [specific domain]; broader deployment would
require [specific additional work].
```

**Common mistakes:**
- Writing "we foresee no negative impacts" (almost never true — reviewers distrust this)
- Being vague: "this could be misused" without specifying how
- Ignoring compute costs for large-scale work
- Forgetting to disclose LLM use at venues that require it

**Compute carbon footprint** (for training-heavy papers):
```python
# Estimate using ML CO2 Impact tool methodology
gpu_hours = 1000  # total GPU hours
gpu_tdp_watts = 400  # e.g., A100 = 400W
pue = 1.1  # Power Usage Effectiveness (data center overhead)
carbon_intensity = 0.429  # kg CO2/kWh (US average; varies by region)

energy_kwh = (gpu_hours * gpu_tdp_watts * pue) / 1000
carbon_kg = energy_kwh * carbon_intensity
print(f"Energy: {energy_kwh:.0f} kWh, Carbon: {carbon_kg:.0f} kg CO2eq")
```

### Step 5.9: Datasheets & Model Cards (If Applicable)

If your paper introduces a **new dataset** or **releases a model**, include structured documentation. Reviewers increasingly expect this, and NeurIPS Datasets & Benchmarks track requires it.

**Datasheets for Datasets** (Gebru et al., 2021) — include in appendix:

```
Dataset Documentation (Appendix):
- Motivation: Why was this dataset created? What task does it support?
- Composition: What are the instances? How many? What data types?
- Collection: How was data collected? What was the source?
- Preprocessing: What cleaning/filtering was applied?
- Distribution: How is the dataset distributed? Under what license?
- Maintenance: Who maintains it? How to report issues?
- Ethical considerations: Contains personal data? Consent obtained?
  Potential for harm? Known biases?
```

**Model Cards** (Mitchell et al., 2019) — include in appendix for model releases:

```
Model Card (Appendix):
- Model details: Architecture, training data, training procedure
- Intended use: Primary use cases, out-of-scope uses
- Metrics: Evaluation metrics and results on benchmarks
- Ethical considerations: Known biases, fairness evaluations
- Limitations: Known failure modes, domains where model underperforms
```

### Step 5.10: Writing Style

**Sentence-level clarity (Gopen & Swan's 7 Principles):**

| Principle | Rule |
|-----------|------|
| Subject-verb proximity | Keep subject and verb close |
| Stress position | Place emphasis at sentence ends |
| Topic position | Put context first, new info after |
| Old before new | Familiar info → unfamiliar info |
| One unit, one function | Each paragraph makes one point |
| Action in verb | Use verbs, not nominalizations |
| Context before new | Set stage before presenting |

**Word choice (Lipton, Steinhardt):**
- Be specific: "accuracy" not "performance"
- Eliminate hedging: drop "may" unless genuinely uncertain
- Consistent terminology throughout
- Avoid incremental vocabulary: "develop", not "combine"

**Full writing guide with examples**: See [references/writing-guide.md](references/writing-guide.md)

### Step 5.11: Using LaTeX Templates

**Always copy the entire template directory first, then write within it.**

```
Template Setup Checklist:
- [ ] Step 1: Copy entire template directory to new project
- [ ] Step 2: Verify template compiles as-is (before any changes)
- [ ] Step 3: Read the template's example content to understand structure
- [ ] Step 4: Replace example content section by section
- [ ] Step 5: Use template macros (check preamble for \newcommand definitions)
- [ ] Step 6: Clean up template artifacts only at the end
```

**Step 1: Copy the Full Template**

```bash
cp -r templates/neurips2025/ ~/papers/my-paper/
cd ~/papers/my-paper/
ls -la  # Should see: main.tex, neurips.sty, Makefile, etc.
```

Copy the ENTIRE directory, not just the .tex file. Templates include style files (.sty), bibliography styles (.bst), example content, and Makefiles.

**Step 2: Verify Template Compiles First**

Before making ANY changes:
```bash
latexmk -pdf main.tex
# Or manual: pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

If the unmodified template doesn't compile, fix that first (usually missing TeX packages — install via `tlmgr install <package>`).

**Step 3: Keep Template Content as Reference**

Don't immediately delete example content. Comment it out and use as formatting reference:
```latex
% Template example (keep for reference):
% \begin{figure}[t]
%   \centering
%   \includegraphics[width=0.8\linewidth]{example-image}
%   \caption{Template shows caption style}
% \end{figure}

% Your actual figure:
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{your-figure.pdf}
  \caption{Your caption following the same style.}
\end{figure}
```

**Step 4: Replace Content Section by Section**

Work through systematically: title/authors → abstract → introduction → methods → experiments → related work → conclusion → references → appendix. Compile after each section.

**Step 5: Use Template Macros**

```latex
\newcommand{\method}{YourMethodName}  % Consistent method naming
\newcommand{\eg}{e.g.,\xspace}        % Proper abbreviations
\newcommand{\ie}{i.e.,\xspace}
```

### Template Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Copying only `.tex` file | Missing `.sty`, won't compile | Copy entire directory |
| Modifying `.sty` files | Breaks conference formatting | Never edit style files |
| Adding random packages | Conflicts, breaks template | Only add if necessary |
| Deleting template content early | Lose formatting reference | Keep as comments until done |
| Not compiling frequently | Errors accumulate | Compile after each section |
| Raster PNGs for figures | Blurry in paper | Always use vector PDF via `savefig('fig.pdf')` |

### Quick Template Reference

| Conference | Main File | Style File | Page Limit |
|------------|-----------|------------|------------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 9 pages |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 8 pages |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 9 pages |
| ACL 2025 | `acl_latex.tex` | `acl.sty` | 8 pages (long) |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 7 pages |
| COLM 2025 | `colm2025_conference.tex` | `colm2025_conference.sty` | 9 pages |

**Universal**: Double-blind, references don't count, appendices unlimited, LaTeX required.

Templates in `templates/` directory. See [templates/README.md](templates/README.md) for compilation setup (VS Code, CLI, Overleaf, other IDEs).

### Tables and Figures

**Tables** — use `booktabs` for professional formatting:

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
Method & Accuracy $\uparrow$ & Latency $\downarrow$ \\
\midrule
Baseline & 85.2 & 45ms \\
\textbf{Ours} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

Rules:
- Bold best value per metric
- Include direction symbols ($\uparrow$ higher better, $\downarrow$ lower better)
- Right-align numerical columns
- Consistent decimal precision

**Figures**:
- **Vector graphics** (PDF, EPS) for all plots and diagrams — `plt.savefig('fig.pdf')`
- **Raster** (PNG 600 DPI) only for photographs
- **Colorblind-safe palettes** (Okabe-Ito or Paul Tol)
- Verify **grayscale readability** (8% of men have color vision deficiency)
- **No title inside figure** — the caption serves this function
- **Self-contained captions** — reader should understand without main text

### Conference Resubmission

For converting between venues, see Phase 7 (Submission Preparation) — it covers the full conversion workflow, page-change table, and post-rejection guidance.

### Professional LaTeX Preamble

Add these packages to any paper for professional quality. They are compatible with all major conference style files:

```latex
% --- Professional Packages (add after conference style file) ---

% Typography
\usepackage{microtype}              % Microtypographic improvements (protrusion, expansion)
                                     % Makes text noticeably more polished -- always include

% Tables
\usepackage{booktabs}               % Professional table rules (\toprule, \midrule, \bottomrule)
\usepackage{siunitx}                % Consistent number formatting, decimal alignment
                                     % Usage: \num{12345} -> 12,345; \SI{3.5}{GHz} -> 3.5 GHz
                                     % Table alignment: S column type for decimal-aligned numbers

% Figures
\usepackage{graphicx}               % Include graphics (\includegraphics)
\usepackage{subcaption}             % Subfigures with (a), (b), (c) labels
                                     % Usage: \begin{subfigure}{0.48\textwidth} ... \end{subfigure}

% Diagrams and Algorithms
\usepackage{tikz}                   % Programmable vector diagrams
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, calc, fit, backgrounds}
\usepackage[ruled,vlined]{algorithm2e}  % Professional pseudocode
                                     % Alternative: \usepackage{algorithmicx} if template bundles it

% Cross-references
\usepackage{cleveref}               % Smart references: \cref{fig:x} -> "Figure 1"
                                     % MUST be loaded AFTER hyperref
                                     % Handles: figures, tables, sections, equations, algorithms

% Math (usually included by conference .sty, but verify)
\usepackage{amsmath,amssymb}        % AMS math environments and symbols
\usepackage{mathtools}              % Extends amsmath (dcases, coloneqq, etc.)

% Colors (for figures and diagrams)
\usepackage{xcolor}                 % Color management
% Okabe-Ito colorblind-safe palette:
\definecolor{okblue}{HTML}{0072B2}
\definecolor{okorange}{HTML}{E69F00}
\definecolor{okgreen}{HTML}{009E73}
\definecolor{okred}{HTML}{D55E00}
\definecolor{okpurple}{HTML}{CC79A7}
\definecolor{okcyan}{HTML}{56B4E9}
\definecolor{okyellow}{HTML}{F0E442}
```

**Notes:**
- `microtype` is the single highest-impact package for visual quality. It adjusts character spacing at a sub-pixel level. Always include it.
- `siunitx` handles decimal alignment in tables via the `S` column type — eliminates manual spacing.
- `cleveref` must be loaded **after** `hyperref`. Most conference .sty files load hyperref, so put cleveref last.
- Check if the conference template already loads any of these (especially `algorithm`, `amsmath`, `graphicx`). Don't double-load.

### siunitx Table Alignment

`siunitx` makes number-heavy tables significantly more readable:

```latex
\begin{tabular}{l S[table-format=2.1] S[table-format=2.1] S[table-format=2.1]}
\toprule
Method & {Accuracy $\uparrow$} & {F1 $\uparrow$} & {Latency (ms) $\downarrow$} \\
\midrule
Baseline         & 85.2  & 83.7  & 45.3 \\
Ablation (no X)  & 87.1  & 85.4  & 42.1 \\
\textbf{Ours}    & \textbf{92.1} & \textbf{90.8} & \textbf{38.7} \\
\bottomrule
\end{tabular}
```

The `S` column type auto-aligns on the decimal point. Headers in `{}` escape the alignment.

### Subfigures

Standard pattern for side-by-side figures:

```latex
\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_a.pdf}
    \caption{Results on Dataset A.}
    \label{fig:results-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_b.pdf}
    \caption{Results on Dataset B.}
    \label{fig:results-b}
  \end{subfigure}
  \caption{Comparison of our method across two datasets. (a) shows the scaling
  behavior and (b) shows the ablation results. Both use 5 random seeds.}
  \label{fig:results}
\end{figure}
```

Use `\cref{fig:results}` -> "Figure 1", `\cref{fig:results-a}` -> "Figure 1a".

### Pseudocode with algorithm2e

```latex
\begin{algorithm}[t]
\caption{Iterative Refinement with Judge Panel}
\label{alg:method}
\KwIn{Task $T$, model $M$, judges $J_1 \ldots J_n$, convergence threshold $k$}
\KwOut{Final output $A^*$}
$A \gets M(T)$ \tcp*{Initial generation}
$\text{streak} \gets 0$\;
\While{$\text{streak} < k$}{
  $C \gets \text{Critic}(A, T)$ \tcp*{Identify weaknesses}
  $B \gets M(T, C)$ \tcp*{Revised version addressing critique}
  $AB \gets \text{Synthesize}(A, B)$ \tcp*{Merge best elements}
  \ForEach{judge $J_i$}{
    $\text{rank}_i \gets J_i(\text{shuffle}(A, B, AB))$ \tcp*{Blind ranking}
  }
  $\text{winner} \gets \text{BordaCount}(\text{ranks})$\;
  \eIf{$\text{winner} = A$}{
    $\text{streak} \gets \text{streak} + 1$\;
  }{
    $A \gets \text{winner}$; $\text{streak} \gets 0$\;
  }
}
\Return{$A$}\;
\end{algorithm}
```

### TikZ Diagram Patterns

TikZ is the standard for method diagrams in ML papers. Common patterns:

**Pipeline/Flow Diagram** (most common in ML papers):

```latex
\begin{figure}[t]
\centering
\begin{tikzpicture}[
  node distance=1.8cm,
  box/.style={rectangle, draw, rounded corners, minimum height=1cm, 
              minimum width=2cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
]
  \node[box, fill=okcyan!20] (input) {Input\\$x$};
  \node[box, fill=okblue!20, right of=input] (encoder) {Encoder\\$f_\theta$};
  \node[box, fill=okgreen!20, right of=encoder] (latent) {Latent\\$z$};
  \node[box, fill=okorange!20, right of=latent] (decoder) {Decoder\\$g_\phi$};
  \node[box, fill=okred!20, right of=decoder] (output) {Output\\$\hat{x}$};
  
  \draw[arrow] (input) -- (encoder);
  \draw[arrow] (encoder) -- (latent);
  \draw[arrow] (latent) -- (decoder);
  \draw[arrow] (decoder) -- (output);
\end{tikzpicture}
\caption{Architecture overview. The encoder maps input $x$ to latent 
representation $z$, which the decoder reconstructs.}
\label{fig:architecture}
\end{figure}
```

**Comparison/Matrix Diagram** (for showing method variants):

```latex
\begin{tikzpicture}[
  cell/.style={rectangle, draw, minimum width=2.5cm, minimum height=1cm, 
               align=center, font=\small},
  header/.style={cell, fill=gray!20, font=\small\bfseries},
]
  % Headers
  \node[header] at (0, 0) {Method};
  \node[header] at (3, 0) {Converges?};
  \node[header] at (6, 0) {Quality?};
  % Rows
  \node[cell] at (0, -1) {Single Pass};
  \node[cell, fill=okgreen!15] at (3, -1) {N/A};
  \node[cell, fill=okorange!15] at (6, -1) {Baseline};
  \node[cell] at (0, -2) {Critique+Revise};
  \node[cell, fill=okred!15] at (3, -2) {No};
  \node[cell, fill=okred!15] at (6, -2) {Degrades};
  \node[cell] at (0, -3) {Ours};
  \node[cell, fill=okgreen!15] at (3, -3) {Yes ($k$=2)};
  \node[cell, fill=okgreen!15] at (6, -3) {Improves};
\end{tikzpicture}
```

**Iterative Loop Diagram** (for methods with feedback):

```latex
\begin{tikzpicture}[
  node distance=2cm,
  box/.style={rectangle, draw, rounded corners, minimum height=0.8cm, 
              minimum width=1.8cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
  label/.style={font=\scriptsize, midway, above},
]
  \node[box, fill=okblue!20] (gen) {Generator};
  \node[box, fill=okred!20, right=2.5cm of gen] (critic) {Critic};
  \node[box, fill=okgreen!20, below=1.5cm of $(gen)!0.5!(critic)$] (judge) {Judge Panel};
  
  \draw[arrow] (gen) -- node[label] {output $A$} (critic);
  \draw[arrow] (critic) -- node[label, right] {critique $C$} (judge);
  \draw[arrow] (judge) -| node[label, left, pos=0.3] {winner} (gen);
\end{tikzpicture}
```

### latexdiff for Revision Tracking

Essential for rebuttals — generates a marked-up PDF showing changes between versions:

```bash
# Install
# macOS: brew install latexdiff (or comes with TeX Live)
# Linux: sudo apt install latexdiff

# Generate diff
latexdiff paper_v1.tex paper_v2.tex > paper_diff.tex
pdflatex paper_diff.tex

# For multi-file projects (with \input{} or \include{})
latexdiff --flatten paper_v1.tex paper_v2.tex > paper_diff.tex
```

This produces a PDF with deletions in red strikethrough and additions in blue — standard format for rebuttal supplements.

### SciencePlots for matplotlib

Install and use for publication-quality plots:

```bash
pip install SciencePlots
```

```python
import matplotlib.pyplot as plt
import scienceplots  # registers styles

# Use science style (IEEE-like, clean)
with plt.style.context(['science', 'no-latex']):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # Single-column width
    ax.plot(x, y, label='Ours', color='#0072B2')
    ax.plot(x, y2, label='Baseline', color='#D55E00', linestyle='--')
    ax.set_xlabel('Training Steps')
    ax.set_ylabel('Accuracy')
    ax.legend()
    fig.savefig('paper/fig_results.pdf', bbox_inches='tight')

# Available styles: 'science', 'ieee', 'nature', 'science+ieee'
# Add 'no-latex' if LaTeX is not installed on the machine generating plots
```

**Standard figure sizes** (two-column format):
- Single column: `figsize=(3.5, 2.5)` — fits in one column
- Double column: `figsize=(7.0, 3.0)` — spans both columns
- Square: `figsize=(3.5, 3.5)` — for heatmaps, confusion matrices
