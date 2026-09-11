import sys
import os
import warnings
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, render_template_string

warnings.filterwarnings("ignore")

from langchain_ollama import ChatOllama
from langchain_community.document_loaders import TextLoader

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sample_resume.txt")

llm = ChatOllama(model="llama3.2", temperature=0.2)

def load_resume():
    return TextLoader(DATA_FILE).load()[0].page_content

def screen_resume_tool(job_role: str, resume_content: str) -> str:
    prompt = f"""Evaluate this candidate against the job role '{job_role}'.
Resume:
{resume_content}

Output format:
1. Match Score (0-100%)
2. Matched Skills (bullet list)
3. Missing Skills (bullet list)
4. Brief Summary Recommendation"""
    return llm.invoke(prompt).content

def generate_interview_questions(job_role: str, resume_content: str) -> str:
    prompt = f"""Generate 4 tailored technical and behavioral interview questions tailored to this candidate for the role: {job_role}.
Resume:
{resume_content}

Format:
Question 1: [Technical] ...
Question 2: [Technical] ...
Question 3: [Behavioral] ...
Question 4: [Problem-Solving] ..."""
    return llm.invoke(prompt).content

# --- Human-Made Web UI Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TalentScan HR - Candidate Screening Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: #f1f5f9;
            color: #1e293b;
            line-height: 1.5;
        }
        .header {
            background-color: #1e293b;
            color: #ffffff;
            padding: 16px 24px;
            border-bottom: 3px solid #0ea5e9;
        }
        .header-content {
            max-width: 1240px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 20px; font-weight: 600; }
        .header p { font-size: 13px; color: #94a3b8; margin-top: 2px; }
        .header-badge {
            background: #334155;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            color: #38bdf8;
            border: 1px solid #475569;
        }
        .container {
            max-width: 1240px;
            margin: 24px auto;
            padding: 0 16px;
            display: grid;
            grid-template-columns: 460px 1fr;
            gap: 24px;
        }
        .card {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .card-header {
            padding: 14px 18px;
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
            font-weight: 600;
            color: #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card-body { padding: 18px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px; }
        input[type="text"], select, textarea {
            width: 100%;
            padding: 10px 12px;
            font-size: 14px;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            outline: none;
            background: #ffffff;
            margin-bottom: 16px;
            font-family: inherit;
        }
        input[type="text"]:focus, select:focus, textarea:focus {
            border-color: #0ea5e9;
            box-shadow: 0 0 0 2px rgba(14,165,233,0.15);
        }
        textarea { height: 190px; resize: vertical; font-family: monospace; font-size: 13px; line-height: 1.4; }
        .btn-screen {
            width: 100%;
            background-color: #0284c7;
            color: #ffffff;
            border: none;
            padding: 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }
        .btn-screen:hover { background-color: #0369a1; }
        .btn-screen:disabled { background-color: #94a3b8; cursor: not-allowed; }
        .section-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 18px;
        }
        .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 6px;
        }
        .output-content {
            white-space: pre-wrap;
            font-size: 13.5px;
            color: #334155;
            line-height: 1.6;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-green { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
        .badge-blue { background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }
        .footer {
            max-width: 1240px;
            margin: 24px auto;
            text-align: center;
            font-size: 12px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <h1>TalentScan HR - Recruitment & Interview Prep Portal</h1>
                <p>Enterprise Talent Operations & Technical Competency Screening</p>
            </div>
            <div class="header-badge">
                Evaluation Model: Ollama llama3.2
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Input Form -->
        <div class="card">
            <div class="card-header">
                Candidate & Job Role Parameters
            </div>
            <div class="card-body">
                <form id="screenForm" onsubmit="evaluateCandidate(event)">
                    <label for="roleInput">Target Job Role / Position:</label>
                    <input type="text" id="roleInput" value="Python Backend Engineer" placeholder="e.g. Python Backend Engineer, DevOps Engineer" required>

                    <label for="rolePreset">Select Common Requisition Presets:</label>
                    <select id="rolePreset" onchange="document.getElementById('roleInput').value = this.value">
                        <option value="Python Backend Engineer">Python Backend Engineer (Default)</option>
                        <option value="Full Stack AI Developer">Full Stack AI Developer</option>
                        <option value="Senior Cloud / DevOps Engineer">Senior Cloud / DevOps Engineer</option>
                        <option value="Data Infrastructure Specialist">Data Infrastructure Specialist</option>
                    </select>

                    <label for="resumeInput">Candidate Resume Content:</label>
                    <textarea id="resumeInput" required>{{ sample_resume }}</textarea>

                    <button type="submit" id="submitBtn" class="btn-screen">Screen Candidate & Generate Interview Guide</button>
                </form>
            </div>
        </div>

        <!-- Evaluation Results Display -->
        <div class="card">
            <div class="card-header">
                <span>Evaluation Scorecard & Technical Assessment</span>
                <span id="statusBadge" class="badge badge-blue">Ready for Assessment</span>
            </div>
            <div class="card-body" id="resultArea">
                <div style="text-align:center; padding: 40px 20px; color:#64748b;">
                    <p style="font-size: 15px; font-weight: 500;">No Candidate Assessment Generated Yet</p>
                    <p style="font-size: 13px; margin-top: 6px;">Select a target job role and click "Screen Candidate" to evaluate skills match and create customized interview questions.</p>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        Talent Acquisition Group &bull; Technical Competency Assessment Framework &bull; Powered by LangChain + Local Ollama
    </div>

    <script>
        async function evaluateCandidate(e) {
            e.preventDefault();
            const role = document.getElementById('roleInput').value.trim();
            const resume = document.getElementById('resumeInput').value.trim();
            const submitBtn = document.getElementById('submitBtn');
            const statusBadge = document.getElementById('statusBadge');
            const resultArea = document.getElementById('resultArea');

            submitBtn.disabled = true;
            submitBtn.innerText = 'Evaluating Candidate Competencies...';
            statusBadge.className = 'badge badge-blue';
            statusBadge.innerText = 'Processing with llama3.2';

            resultArea.innerHTML = `
                <div style="text-align:center; padding: 50px 20px; color:#64748b;">
                    <p style="font-size: 15px; font-weight: 600; color: #0284c7;">Analyzing Candidate Against Job Role...</p>
                    <p style="font-size: 13px; margin-top: 6px;">Running match scoring rubric and tailoring interview questions using local LLM.</p>
                </div>
            `;

            try {
                const res = await fetch('/api/screen', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ role, resume })
                });
                const data = await res.json();
                if (data.evaluation && data.questions) {
                    statusBadge.className = 'badge badge-green';
                    statusBadge.innerText = 'Evaluation Complete';
                    resultArea.innerHTML = `
                        <div class="section-box">
                            <div class="section-title">Resume Screening & Match Evaluation</div>
                            <div class="output-content">${escapeHtml(data.evaluation)}</div>
                        </div>
                        <div class="section-box" style="margin-bottom:0;">
                            <div class="section-title">Tailored Technical & Behavioral Interview Questions</div>
                            <div class="output-content">${escapeHtml(data.questions)}</div>
                        </div>
                    `;
                } else {
                    resultArea.innerHTML = '<p style="color:red;">Error processing evaluation response.</p>';
                }
            } catch (err) {
                resultArea.innerHTML = '<p style="color:red;">Network or server error occurred.</p>';
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = 'Screen Candidate & Generate Interview Guide';
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.innerText = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

# --- Flask Server & CLI Switch ---
app = Flask(__name__)

@app.route("/")
def index():
    resume_content = load_resume()
    return render_template_string(HTML_TEMPLATE, sample_resume=resume_content)

@app.route("/api/screen", methods=["POST"])
def api_screen():
    data = request.get_json() or {}
    role = data.get("role", "Python Backend Engineer").strip()
    resume_content = data.get("resume", "").strip() or load_resume()

    evaluation = screen_resume_tool(role, resume_content)
    questions = generate_interview_questions(role, resume_content)

    return jsonify({
        "evaluation": evaluation,
        "questions": questions
    })

def run_cli():
    resume = load_resume()
    role = input("Enter target Job Role (e.g., Python Backend Engineer): ")
    print("\n--- Screening Resume ---")
    evaluation = screen_resume_tool(role, resume)
    print(evaluation)
    print("\n--- Generated Custom Interview Questions ---")
    questions = generate_interview_questions(role, resume)
    print(questions)

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        port = 5002
        print(f"==========================================================")
        print(f" TalentScan HR Recruitment Portal Active")
        print(f" URL: http://127.0.0.1:{port}")
        print(f" Running with LangChain + Ollama (llama3.2)")
        print(f" (To run in CLI mode instead, execute: python app.py --cli)")
        print(f"==========================================================")
        Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
        app.run(host="127.0.0.1", port=port, debug=False)
