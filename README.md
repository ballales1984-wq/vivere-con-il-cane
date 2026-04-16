# 🐕 Vivere con il Cane (Living with your Dog) - AI HealthTech Platform

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![AI](https://img.shields.io/badge/AI-Groq%20Llama%203-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

*🌍 [Leggi la documentazione in Italiano](README.it.md)*

**Vivere con il Cane** is not just a blog—it is a modern, AI-powered HealthTech platform designed for dog owners. It acts as a **24/7 Virtual Veterinary Assistant** capable of cross-referencing a dog's complete medical and behavioral history to provide highly personalized, context-aware advice. 

---

## 🌟 Unique Value Proposition (UVP)

### 🧠 1. Longitudinal Memory & Dynamic Prompt Routing
Unlike standard LLM wrappers, our AI engine (powered by Llama-3 70B via Groq) features **contextual routing**. 
- It maintains a **Longitudinal Memory** of your dog's profile (exact age, weight, and past conditions).
- Before pinging the LLM, the backend dynamically constructs a "Super-Prompt" injecting the active dog's medical history. 
- *Result:* When you type "limping", the AI knows it's treating a *10-year-old overweight dog with previous arthritis history*, yielding 10x more accurate and safe vet-like responses.

### 📋 2. Comprehensive Medical Dossier (Vet-Ready)
- Generates a unified **Clinical History Timeline** that merges physical health events (vaccines, checkups) with past AI behavioral/diagnostic consultations.
- Designed for immediate real-world use: features a 1-click **WhatsApp export**, plain-text clipboard copying, and a distraction-free **Print to PDF** view optimized for sending to veterinarians.

### 📚 3. Relational Symptoms-to-Causes Matrix
This isn't a traditional flat database or a simple blog. The Knowledge Base is a relational matrix:
- **Behaviors/Symptoms**, **Root Causes**, and **Actionable Solutions** are tightly coupled in the backend. 
- Allows the AI logic to surgically pinpoint *why* a problem is happening based on the dog's stored breed matrix (energy levels, hereditary traits) and suggest difficulty-rated solutions.

### 📈 4. SEO-Optimized HealthTech Hub
- Beyond the AI application, the platform functions as an educational portal fully injected with **Schema.org JSON-LD** structured data.
- Glassmorphism UI, gradient aesthetics, and premium dynamic CTAs designed to convert regular readers into active users of the AI diagnosis tool.


## 🏗️ Architecture

```mermaid
graph TD
    User([User]) -->|Interacts| UI[Frontend UI/Templates]
    UI -->|Saves Profile & Queries AI| Core(Django Backend)
    
    subgraph Data Layer
        Core --> DB[(SQLite / PostgreSQL)]
        DB -->|Dogs| Profiles[Dog Profiles]
        DB -->|Articles| Blog[SEO Blog]
        DB -->|Symptoms/Breeds| KB[Knowledge Base]
    end
    
    Core <-->|Context-Rich Prompting| AI[Groq API / Llama 3]
    AI -->|Diagnostic Output| UI
```

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Django 5+
- **Frontend**: Django Templates, Raw CSS variables, Glassmorphism UI
- **AI Integration**: Custom agentic prompt construction via Groq REST API
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Deployment**: Render, WhiteNoise for static file serving

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   cd vivere-con-il-cane
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   SECRET_KEY=your_secret_key
   GROK_API_KEY=your_groq_api_key_here
   ```

5. **Database Initialization & Fixtures**
   ```bash
   python manage.py migrate
   
   # Load high-quality sample data matrices
   python manage.py loaddata blog/fixtures/blog_data.json
   python manage.py loaddata knowledge/fixtures/knowledge_data.json
   ```

6. **Run the Application**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000` to interact with the platform.

---

## 💡 How the AI Reasoning Engine Works

When a user asks a question (e.g., "My dog is limping"), the backend doesn't just forward the question. It builds a **context-rich super-prompt**:
1. Fetches the active Dog Profile (e.g., "Prince, 10 years old, Mixed Breed").
2. Retrieves past analyses (e.g., "Has a history of incontinence").
3. Retrieves relevant Knowledge Base snippets (e.g., "Arthritis in older dogs").
4. Sends the packaged context to the LLM.
*Result*: The AI returns a response that accounts for age, weight, and past medical history, simulating a real veterinary diagnostic workflow.

---

## 🤝 Contributing
Contributions are highly welcome. This project aims to democratize high-quality canine health information.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.