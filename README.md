# Precision-NutriFuzzy-AI 🥗
### *Advanced Research in Personalized Nutrition & Intelligent Decision Support Systems*

---

## 🔬 Abstract
Current dietary recommendation systems often rely on rigid, boolean logic (e.g., "If Age > 30, then X"). In contrast, **Precision-NutriFuzzy-AI** presents an intelligent nutritional advisory engine designed to model the inherent stochasticity and "fuzzy" boundaries of human physiology. By leveraging **Gaussian Fuzzy Membership Functions** and multi-dimensional biometric mapping, the system reconciles clinical dietary guidelines with individual metabolic profiles, offering a scalable, high-precision solution for preventative healthcare and chronic disease management.

---

## 🧠 Technical Methodology

### 1. Fuzzy Logic & Gaussian Membership
The core novelty of this system lies in its departure from traditional 'crisp' classification. Human health data (Age, Height, Weight) exists on a continuum. We implement **Gaussian Fuzzy Sets** to represent user attributes:
- **Membership Function**: $\mu(x) = \exp\left(-\frac{1}{2}\left(\frac{x - c}{\sigma}\right)^2\right)$
- This allows the system to calculate a "similarity score" between the user's profile and established clinical archetypes, handling edge cases far more effectively than standard algorithms.

### 2. High-Density Knowledge Base
The system's intelligence is synthesized from a corpus of authoritative medical and nutritional references:
- **Clinical Therapy for Specific Diseases**: Management of chronic conditions (Diabetes, Hypertension, etc.).
- **ICMR-National Institute of Nutrition (NIN)**: Regional and global dietary standards.
- **World Health Organization (WHO)**: Global nutritional benchmarks.
- **Biotechnological Insights**: Integration of simulated genetic markers and microbiome profiles to explore the frontier of nutrigenomics.

---

## 🚀 Key Features & Research Highlights
- **🧬 Biometric Signature Mapping**: Analyzes Age, Height, Weight, and Clinical History to generate a unique nutritional profile.
- **🔍 Intelligent Heuristics**: Utilizes `fuzzywuzzy` string-matching algorithms to normalize clinical terminology and disease naming conventions.
- **🏥 Medical Context Reconciliation**: Cross-references multiple authoritative datasets ([1.json](1.json), [3.json], [4.json]) to ensure clinical safety and nutritional accuracy.
- **🍎 Automated Diet Synthesis**: Generates complete daily menus (Breakfast, Lunch, Dinner) tailored to nutrient focus and genetic profiles.
- **🎨 Research Dashboard**: A premium **Streamlit** interface for real-time interaction and data visualization.

---
## App Layout
![App Layout 1](app%20layout.png)
![App Layout 2](app%20layout2.png)


## 🛠️ Technology Stack
- **Language**: Python 3.10+
- **Mathematics**: NumPy (Gaussian Distributions, Vectorized Similarity Calculations)
- **Natural Language Processing**: Fuzzy-matching algorithms for clinical data normalization.
- **Frontend**: Streamlit (Advanced UI with Glassmorphism aesthetics)
- **Data Architecture**: High-density structured JSON Knowledge Base.

---

## 📂 System Architecture
- `app.py`: The primary Research Dashboard and Interaction Layer.
- `fullde.py`: The underlying logic engine and similarity computation core.
- `1.json`, `3.json`: Clinical guidelines for chronic disease management.
- `5gpt.json`: High-precision profile-based nutritional plans.
- `6web.json`: Advanced dataset for genetic and microbiome-based insights.

---

## 📈 Future Research Directions
This project serves as a foundational prototype for:
1. **IoT Integration**: Real-time glucose/heart-rate monitoring for dynamic diet adjustments.
2. **Deep Learning Refinement**: Transitioning from fuzzy logic to transformer-based nutritional forecasting.
3. **Clinical Validation**: Collaboration with dietitian cohorts to refine the heuristic weights.

---

## ⚙️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Precision-NutriFuzzy-AI.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```
Developed by**: Naina  
**Guided by**: Prof. Rohit Kumar  
---
*Created for academic excellence and research impact.*
