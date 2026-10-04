# Snap & Study 📚

An intelligent, multi-modal AI study assistant powered by Groq and Streamlit. Snap notes, textbook pages, homework questions, or whiteboard diagrams to get instant, student-friendly explanations, high-yield summaries, flashcards, practice quizzes, and step-by-step problem solutions.

---

## ✨ Features

- 📸 **Live Camera Snap & Image Upload**:
  - Direct webcam/camera capture with one click.
  - Multi-format file uploader (`PNG`, `JPG`, `JPEG`, `WEBP`) with drag-and-drop.
  - Chat input with integrated photo attachment.
- ⚡ **Ultra-Fast Real-Time Streaming**:
  - Live token streaming via Groq LPU inference (`qwen/qwen3.8-27b` for vision/multimodal OCR, and `openai/gpt-oss-120b` for deep reasoning) for near-instant answers.
- 🎯 **Personalized Tutor Personas**:
  - **Encouraging Socratic Coach**: Guides you with hints rather than just giving away solutions.
  - **Peer Study Buddy**: Easy ELI5 analogies, casual and friendly.
  - **Detailed Professor**: Rigorous, formal academic depth.
  - **High-Yield Crammer**: Bullet points, mnemonics, and exam trap alerts.
- 🎓 **Target Academic Levels**:
  - Middle School, High School (AP/IB/GCSE/CBSE), College/Undergrad, Graduate/Competitive Exams (SAT/JEE/NEET/GRE).
- 📇 **One-Click Study Tools**:
  - 🔍 **Explain**: Intuitive concept explanations with real-world examples.
  - ⚡ **Summary**: High-yield exam takeaways, definitions, and key takeaways.
  - 📇 **Flashcards**: Front/Back interactive Q&A cards.
  - 🎯 **Practice Quiz**: 3 diagnostic multiple-choice questions with answer checks.
  - 🧮 **Step-by-Step Solver**: Complete derivations with clean **LaTeX** math ($$...$$).
- 📥 **Export Study Notes**:
  - Download full study transcripts and summaries as Markdown (`.md`) files.
- 🎨 **Modern Sleek UI**:
  - Dark-mode glassmorphic theme with responsive layout and clean typography.

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Groq API Key
Get your free API key from the [GroqCloud Console](https://console.groq.com/keys).

Create or edit `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
```
*(You can also input your API key directly in the app's sidebar or set the `GROQ_API_KEY` environment variable).*

### 3. Run the App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.
