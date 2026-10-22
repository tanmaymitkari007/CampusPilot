# CampusPilot 🎓

**Your campus information, organized into actionable tasks.**

CampusPilot is an AI-assisted academic task extraction project designed to help students keep track of assignments, exams, workshops, registration deadlines, and other important academic updates shared across busy messaging groups.

Instead of manually searching through long chat exports, CampusPilot analyzes an exported WhatsApp chat ZIP and extracts candidate tasks with relevant deadlines and supporting evidence.

> **Project status:** Hackathon / development project. Verify extracted tasks and dates against the original messages before relying on them.

## ✨ Features

- **WhatsApp export analysis** — upload a ZIP containing an exported chat and analyze its messages.
- **AI-assisted task extraction** — use the configured Gemma-based pipeline to identify academic tasks and deadlines.
- **Deadline tracking** — organize extracted tasks by deadline and urgency.
- **Conflict visibility** — surface potentially conflicting or rescheduled deadlines instead of silently discarding relevant versions.
- **Evidence and warnings** — retain supporting message evidence and extraction warnings where available.
- **Task dashboard** — review tasks, search and filter results, and mark tasks as pending or completed.
- **Extraction status** — display analysis metadata and report partial extraction failures where returned by the backend.

Feature availability depends on the current implementation and the response returned by the backend.

## 🧰 Tech Stack

| Component | Technology |
| --- | --- |
| Frontend | React, Vite, CSS |
| Backend | Python, FastAPI |
| AI task extraction | Gemma-based model pipeline |
| Input | Exported WhatsApp chat ZIP |
| API | HTTP endpoints served by FastAPI |

## 📁 Project Structure

```text
CampusPilot/
├── backend/
│   └── ...              # FastAPI application and analysis pipeline
├── frontend/
│   ├── src/
│   │   └── ...          # React application
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

The exact contents may evolve as development continues.

## ⚙️ Prerequisites

Install the following before running the project:

- Python 3.10 or a compatible version supported by the backend dependencies
- Node.js and npm
- Git
- Access to the configured Gemma inference provider or local model runtime
- Any model credentials required by your chosen inference configuration

Model availability, hardware requirements, and credentials depend on the backend configuration.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd CampusPilot
```

Replace `<YOUR_PUBLIC_REPOSITORY_URL>` with your repository's HTTPS or SSH clone URL.

### 2. Set up the backend

From the project root, create and activate a Python virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies using the dependency file included in the repository. For example, if the project has `backend/requirements.txt`:

```powershell
pip install -r backend/requirements.txt
```

If your repository stores its requirements file elsewhere, use its actual path instead.

Configure the environment variables required by your backend and selected model provider. Consult the backend configuration and source code for the exact variable names.

Do not commit API keys, access tokens, private chat exports, or other secrets.

### 3. Start the backend

From the project root, if the FastAPI application entry point is `backend/main.py` and exposes `app`:

```powershell
uvicorn main:app --app-dir backend --reload
```

The local API will normally be available at:

- API base: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

These URLs assume the default local development configuration. If the application uses a different host, port, or route, follow its configuration.

### 4. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, commonly `http://localhost:5173`.

If the frontend API URL is configurable, ensure it points to the running backend.

## 📝 How to Use

1. Start the backend and frontend.
2. Export the relevant WhatsApp conversation using WhatsApp's export-chat feature.
3. Prepare the exported chat ZIP in the format accepted by the application.
4. Upload the ZIP through the CampusPilot dashboard.
5. Wait for the analysis to complete.
6. Review extracted tasks, deadlines, supporting evidence, warnings, and possible conflicts.
7. Verify important dates against the original messages before acting on them.
8. Track tasks as pending or completed in the dashboard.

The exact upload format and extraction behavior are determined by the current backend implementation.

## 🔍 Accuracy and Limitations

CampusPilot uses AI to interpret messages, which means it can miss tasks, misunderstand context, infer an incorrect date, or flag a conflict that needs human review.

- Treat extracted deadlines as suggestions until verified.
- Pay particular attention to implicit years, edited announcements, cancellations, and rescheduled events.
- Review partial extraction warnings and failed batches.
- Do not assume that an absent task means no deadline exists in the source conversation.
- Avoid uploading sensitive conversations unless you understand where the data is processed and stored.
- Do not rely on CampusPilot as the sole source of truth for academic submissions or examinations.

## 🔐 Privacy and Security

WhatsApp exports can contain personal information. Use only conversations you are authorized to process.

Before sharing or deploying this project:

- Keep API keys and secrets in environment variables or an ignored local environment file.
- Never commit real chat exports, test archives containing private messages, tokens, or credentials.
- Review model-provider data handling and retention policies.
- Review backend logging and storage behavior before processing other people's data.
- Configure appropriate authentication, access controls, and network exposure before making a deployment publicly accessible.

A local development server is not automatically a secure public deployment.

## 🛠️ Troubleshooting

**The frontend cannot reach the backend**
- Confirm the backend is running.
- Check the API URL and port configured in the frontend.
- Open `/health` and inspect the backend terminal for errors.

**Analysis returns partial results**
- Inspect the analysis status, warnings, and extraction errors.
- Retry with a smaller or simpler test export if appropriate.
- Check the configured model provider or local inference runtime and its timeout settings.

**No tasks are extracted**
- Confirm the ZIP is in the format accepted by the application.
- Check backend logs and model configuration.
- Test with a small export containing clear, explicit task announcements.

**The model is unavailable**
- Verify the configured provider, model identifier, credentials, and network or local-runtime requirements.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Open a pull request describing the changes and any relevant testing.

Please avoid including secrets, private conversations, or personally identifiable information in issues, pull requests, and test fixtures.

By submitting a contribution, you agree that your contribution may be distributed under the repository's MIT License, unless a different arrangement is explicitly agreed upon.

## 📜 License

CampusPilot is released under the **MIT License**. See [`LICENSE`](LICENSE) for the complete license text.

The MIT License applies to the project code and other material owned by the copyright holder. Third-party dependencies, models, datasets, and external services remain subject to their respective licenses and terms.

## 🙌 Acknowledgements

CampusPilot is a student-built project exploring how AI can help students manage fragmented academic announcements and deadlines.
