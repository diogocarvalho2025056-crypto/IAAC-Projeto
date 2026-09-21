# Machine Learning Canvas & Deep Data Understanding (CRISP-ML Phase 1 & 2)

---

## 1. Machine Learning Canvas (Business Understanding)

### 1.1. Value Proposition & Business Goal
* **Problem Statement:** Modern ransomware attacks execute in milliseconds, encrypting critical corporate infrastructure before traditional signature-based antiviruses detect them.
* **Objective:** Build an automated Machine Learning pipeline to perform real-time binary classification (`Malware` vs. `Benign`) on Portable Executable (`.exe`) files based on static PE Header parameters and dynamic sandbox behavior.
* **Value Created:** Reduces Security Operations Center (SOC) Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR) by classifying unknown binaries and automatically synthesizing incident reports via a generative Multi-Agent LLM.

### 1.2. Machine Learning Task
* **Task Type:** Supervised Binary Classification.
* **Target Variable:** `Class` (`Malware` = 1, `Benign` = 0).
* **Secondary Targets (Future Iteration):** `Category` (Multi-class) and `Family` (e.g., *LockBit*, *WannaCry*, *Phobos*).
* **Inputs:** 74 structural PE Header characteristics (hexadecimal values, compiled section flags) and dynamic execution traces (registry modifications, process creation, network calls).

### 1.3. Decision Making & Integration
* **Trigger:** A end-user downloads an executable or a file is flagged by network monitoring.
* **Action Pipeline:**
  1. Feature extraction engine parses PE Headers and sandbox metrics.
  2. Scikit-learn classification model evaluates risk probability.
  3. If $P(\text{Malware}) \ge \text{Threshold}$, isolate endpoint and trigger the **Generative Security LLM Agent** to issue an automated incident report.

### 1.4. Operational Constraints & Trade-offs
* **Latency vs. Accuracy:** Dynamic metrics (`registry_read`, `processes_malicious`) require sandbox execution, introducing latency (1–3 minutes). Static PE features can evaluate instantly (milliseconds).
* **Asymmetric Risk Costs:**
  * **False Negative (FN) Cost = Extremely High:** A ransomware sample bypasses detection, leading to system encryption and data exfiltration.
  * **False Positive (FP) Cost = Moderate:** A legitimate binary is quarantined; requires administrator review.
* **Key Metric:** **Recall on Malware Class** must be optimized ($\ge 0.99$) alongside $F_1\text{-score}$.

---

## 2. Formal Data Understanding & Mathematical Foundations

### 2.1. Dataset Overview & Schema
* **File:** `data/raw/ransom.csv`
* **Observations ($N$):** $21{,}752$
* **Features ($P$):** $77$ columns ($2$ hash identifiers + $72$ feature attributes + $3$ target columns).
* **Missing Values:** $0$
* **Class Balance:** Perfectly balanced — $10{,}876$ Benign ($50.0\%$), $10{,}876$ Malware ($50.0\%$).

### 2.2. Mathematical Analysis of Features & Distributions

#### Univariate Analysis
Let $X_j$ represent feature $j$. Key distributional properties are evaluated using Skewness ($S$) and Excess Kurtosis ($K$):

$$S(X_j) = \frac{\mathbb{E}[(X_j - \mu_j)^3]}{\sigma_j^3}, \quad K(X_j) = \frac{\mathbb{E}[(X_j - \mu_j)^4]}{\sigma_j^4} - 3$$

* **Dynamic Features (`total_procsses`, `files_malicious`, `registry_write`):** Exhibit severe positive skewness ($S > 3.0$) and heavy tails ($K > 10.0$), indicating that benign binaries rarely spawn abnormal background processes, whereas specific malware families generate massive activity bursts.
* **PE Header Static Features (`SizeOfCode`, `SizeOfImage`):** Exhibit multi-modal distributions due to different compiler toolchains (MSVC, GCC) and packing techniques (UPX, ASPack).

#### Bivariate Analysis & Correlation Metrics

To measure linear and monotonic relationships between features $X$ and target $Y$:

1. **Pearson Correlation Coefficient ($\rho$):**
$$\rho_{X,Y} = \frac{\sum_{i=1}^{N} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}$$

2. **Spearman Rank Correlation ($\rho_s$):**
$$\rho_s = 1 - \frac{6 \sum d_i^2}{N(N^2 - 1)}$$

*Top Pearson/Spearman Correlations with Target (`Malware = 1`):*
* `total_procsses` ($\rho = +0.206$): Strong positive indicator of malicious process spawning.
* `files_text` ($\rho = +0.186$): Reflects log creation or note drop activities (e.g., ransom notes).
* `files_malicious` ($\rho = +0.182$): Direct sandbox indicator.
* `rdata_PointerToRawData` ($\rho = -0.133$): Structural offset differences caused by packed `.rdata` sections.

*Statistical Note:* Low-to-moderate linear correlations across single attributes indicate that **non-linear tree ensemble algorithms (Random Forest, XGBoost)** are required to learn complex conditional interactions:

$$P(\text{Malware} \mid \text{PE Header}, \text{Sandbox Traces})$$

#### Probabilistic & Bayesian Foundation

Using Bayes' Theorem, the posterior probability of a binary being malware given its feature vector $\mathbf{x}$ is:

$$P(\text{Malware} \mid \mathbf{x}) = \frac{P(\mathbf{x} \mid \text{Malware}) \cdot P(\text{Malware})}{P(\mathbf{x})}$$

Since $P(\text{Malware}) = P(\text{Benign}) = 0.50$, the decision boundary simplifies to comparing the likelihood ratios:

$$\Lambda(\mathbf{x}) = \frac{P(\mathbf{x} \mid \text{Malware})}{P(\mathbf{x} \mid \text{Benign})} > 1 \implies \text{Classify as Malware}$$

---

## 3. Data Quality, Data Leakage & Engineering Action Plan

1. **Hash Column Removal:** `md5` and `sha1` represent unique cryptographic signatures. Retaining them induces memory leakage. Action: Drop immediately in `make_dataset.py`.
2. **Sub-target Exclusion:** `Category` and `Family` provide granular classification but leak the binary's underlying nature during binary evaluation. Action: Isolate in feature builder.
3. **Hexadecimal String Parsing:** Attributes like `EntryPoint`, `ImageBase`, and `SizeOfCode` are formatted as hex strings (e.g., `0x00011200`). Action: Convert to base-10 numerical representations in `build_features.py`.
4. **Flag List Aggregation:** Attributes such as `DllCharacteristics` contain string lists of compilation flags. Action: Parse list length and apply one-hot encoding to safety features (e.g., `IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE` / ASLR).