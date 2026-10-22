import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/analyze";

const navItems = [
  ["▦", "Overview"],
  ["✓", "Tasks"],
  ["◷", "Deadlines"],
  ["⚠", "Conflicts"],
];

function normalizeTask(task, index) {
  const score = Number(task.priority_score ?? 0);
  const rawPriority = String(task.priority ?? "").toLowerCase();
  let priority = "Medium";

  if (rawPriority.includes("critical") || rawPriority.includes("urgent") || score >= 4) {
    priority = "Critical";
  } else if (
    rawPriority.includes("high") ||
    String(task.urgency ?? "").toLowerCase().includes("due soon") ||
    score >= 3
  ) {
    priority = "High";
  } else if (rawPriority.includes("low") || score <= 1) {
    priority = "Low";
  }

  const warnings = Array.isArray(task.warnings)
    ? task.warnings.filter(Boolean).map(String)
    : [];

  return {
    id: `${task.source?.source_file ?? "task"}-${task.source_message_ids?.join("-") ?? "msg"}-${task.deadline ?? "no-date"}-${index}`,
    title: String(task.title || "Untitled task"),
    description: String(task.description || ""),
    category: String(task.category || "Other"),
    deadline: String(task.deadline || ""),
    deadlineText: String(task.deadline_text || ""),
    priority,
    priorityScore: score,
    urgency: String(task.urgency || ""),
    status: "Pending",
    evidence: String(task.evidence || task.source_text || ""),
    warnings,
    conflict: Boolean(task.conflict),
    possibleDuplicate: Boolean(task.possible_duplicate),
    source: task.source || {},
    sourceMessageIds: Array.isArray(task.source_message_ids) ? task.source_message_ids : [],
  };
}

function formatDeadline(task) {
  if (task.deadlineText) return task.deadlineText;
  if (!task.deadline) return "Not specified";

  const parsed = new Date(`${task.deadline}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return task.deadline;
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(parsed);
}

function getTodayISO() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function App() {
  const [tasks, setTasks] = useState([]);
  const [activeNav, setActiveNav] = useState("Overview");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [file, setFile] = useState(null);
  const [uploadState, setUploadState] = useState("idle");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [analysisSummary, setAnalysisSummary] = useState(null);

  useEffect(() => {
    if (uploadState !== "processing") {
      setElapsedSeconds(0);
      return undefined;
    }

    const startedAt = Date.now();
    const timer = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [uploadState]);

  const today = getTodayISO();

  const pending = tasks.filter((task) => task.status === "Pending").length;
  const completed = tasks.filter((task) => task.status === "Completed").length;
  const overdueOrToday = tasks.filter(
    (task) => task.status === "Pending" && task.deadline && task.deadline <= today
  ).length;
  const conflictCount = tasks.filter((task) => task.conflict).length;

  const filteredTasks = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return tasks.filter((task) => {
      const searchable = [
        task.title,
        task.category,
        task.description,
        task.evidence,
        task.deadline,
        task.deadlineText,
        ...task.warnings,
      ]
        .join(" ")
        .toLowerCase();

      const matchesSearch = !normalizedSearch || searchable.includes(normalizedSearch);
      const matchesStatus =
        filter === "All" ||
        (filter === "Pending" && task.status === "Pending") ||
        (filter === "Completed" && task.status === "Completed");

      const matchesNav =
        activeNav === "Conflicts"
          ? task.conflict
          : activeNav === "Deadlines"
            ? Boolean(task.deadline)
            : true;

      return matchesSearch && matchesStatus && matchesNav;
    });
  }, [tasks, search, filter, activeNav]);

  function toggleTask(id) {
    setTasks((current) =>
      current.map((task) =>
        task.id === id
          ? { ...task, status: task.status === "Completed" ? "Pending" : "Completed" }
          : task
      )
    );
  }

  async function analyzeExport() {
    if (!file || uploadState === "processing") return;

    setUploadState("processing");
    setErrorMessage("");
    setAnalysisSummary(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      let result;
      try {
        result = await response.json();
      } catch {
        throw new Error(`The backend returned an unreadable response (HTTP ${response.status}).`);
      }

      if (!response.ok) {
        const detail = typeof result.detail === "string"
          ? result.detail
          : JSON.stringify(result.detail || result);
        throw new Error(detail || `Analysis failed (HTTP ${response.status}).`);
      }

      if (!Array.isArray(result.tasks)) {
        throw new Error("The backend response did not contain a tasks array.");
      }

      const normalizedTasks = result.tasks.map(normalizeTask);
      setTasks(normalizedTasks);
      setAnalysisSummary({
        messageCount: result.message_count,
        calendarDays: result.calendar_days,
        batchesTotal: result.batches_total,
        providersUsed: Array.isArray(result.providers_used) ? result.providers_used : [],
        extractionErrors: Array.isArray(result.extraction_errors) ? result.extraction_errors : [],
        serverStatus: result.status || "completed",
      });

      const hasErrors =
        (Array.isArray(result.extraction_errors) && result.extraction_errors.length > 0) ||
        result.status === "partial";
      setUploadState(hasErrors ? "partial" : "success");
      setActiveNav("Overview");
      setFilter("All");
      setSearch("");
    } catch (error) {
      console.error("CampusPilot analysis failed:", error);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Analysis failed. Check that the backend is running."
      );
      setUploadState("error");
    }
  }

  const heading =
    activeNav === "Overview"
      ? "Good afternoon."
      : activeNav === "Conflicts"
        ? "Potential conflicts"
        : activeNav;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => event.preventDefault()}>
          <span className="brand-mark">C</span>
          <span>Campus<span className="brand-light">Pilot</span></span>
        </a>

        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navItems.map(([icon, label]) => (
            <button
              key={label}
              className={`nav-item ${activeNav === label ? "active" : ""}`}
              onClick={() => setActiveNav(label)}
              type="button"
            >
              <span className="nav-icon" aria-hidden="true">{icon}</span>
              {label}
              {label === "Tasks" && <span className="nav-count">{pending}</span>}
              {label === "Conflicts" && conflictCount > 0 && (
                <span className="nav-count">{conflictCount}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>CampusPilot AI</strong>
            <p>Announcement intelligence</p>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {activeNav}</div>
          <div className="topbar-right">
            <span className="ai-badge"><span /> AI SYSTEM</span>
            <div className="avatar" aria-label="User profile">TP</div>
          </div>
        </header>

        <section className="page-content">
          <div className="page-heading">
            <div>
              <p className="eyebrow">YOUR CAMPUS, ORGANIZED</p>
              <h1>{heading}</h1>
              <p className="subtitle">
                All your college updates, deadlines, and tasks in one place.
              </p>
            </div>
            <button
              className="primary-button"
              type="button"
              onClick={() => document.getElementById("zip-upload")?.click()}
            >
              <span>＋</span> Import WhatsApp
            </button>
          </div>

          <section className="stats-grid" aria-label="Task summary">
            <StatCard label="Pending tasks" value={pending} note="Awaiting action" icon="✓" />
            <StatCard label="Due today / overdue" value={overdueOrToday} note="Needs attention" icon="◷" />
            <StatCard label="Completed" value={completed} note="Tasks finished" icon="↗" />
            <StatCard label="Potential conflicts" value={conflictCount} note="Review flagged dates" icon="⚠" />
          </section>

          <section className="import-panel">
            <div className="import-icon" aria-hidden="true">↑</div>
            <div className="import-copy">
              <h3>Bring your campus updates together</h3>
              <p>Upload a WhatsApp chat export ZIP to extract tasks and deadlines.</p>
              {file && <p className="selected-file">Selected: {file.name}</p>}
              {uploadState === "processing" && (
                <p className="processing-text" role="status" aria-live="polite">
                  <span className="spinner" />
                  Analyzing messages… {Math.floor(elapsedSeconds / 60)}m{" "}
                  {elapsedSeconds % 60}s elapsed. Keep this page open.
                </p>
              )}
              {uploadState === "success" && (
                <p className="success-text">
                  Analysis completed — {tasks.length} task{tasks.length === 1 ? "" : "s"} found.
                </p>
              )}
              {uploadState === "partial" && (
                <p className="warning-text">
                  Analysis finished with some extraction errors. Showing the tasks that were recovered.
                </p>
              )}
              {uploadState === "error" && (
                <p className="error-text">
                  {errorMessage || "Analysis failed. Check that the backend is running."}
                </p>
              )}
              {analysisSummary && (
                <div className="analysis-meta">
                  {Number.isFinite(Number(analysisSummary.messageCount)) && (
                    <span>{analysisSummary.messageCount} messages</span>
                  )}
                  {Number.isFinite(Number(analysisSummary.calendarDays)) && (
                    <span>{analysisSummary.calendarDays} chat days</span>
                  )}
                  {analysisSummary.providersUsed.length > 0 && (
                    <span>Model: {analysisSummary.providersUsed.join(", ")}</span>
                  )}
                </div>
              )}
              {analysisSummary?.extractionErrors?.length > 0 && (
                <details className="error-details">
                  <summary>View {analysisSummary.extractionErrors.length} extraction warning(s)</summary>
                  <ul>
                    {analysisSummary.extractionErrors.map((error, index) => (
                      <li key={`${index}-${String(error)}`}>
                        {typeof error === "string" ? error : JSON.stringify(error)}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
            <input
              id="zip-upload"
              type="file"
              accept=".zip,application/zip"
              hidden
              onChange={(event) => {
                setFile(event.target.files?.[0] || null);
                setUploadState("idle");
                setErrorMessage("");
                setAnalysisSummary(null);
              }}
            />
            <button
              className="secondary-button"
              type="button"
              disabled={!file || uploadState === "processing"}
              onClick={analyzeExport}
            >
              {uploadState === "processing" ? "Analyzing…" : "Analyze export →"}
            </button>
          </section>

          <section className="tasks-section">
            <div className="section-heading">
              <div>
                <h2>
                  {activeNav === "Conflicts"
                    ? "Flagged task conflicts"
                    : activeNav === "Deadlines"
                      ? "Tasks with deadlines"
                      : activeNav === "Tasks"
                        ? "All tasks"
                        : "Priority tasks"}
                </h2>
                <p>
                  {activeNav === "Conflicts"
                    ? "Check the source messages before deciding which date is correct."
                    : "Review extracted tasks and mark them complete as you go."}
                </p>
              </div>
              <span className="task-total">{filteredTasks.length} shown / {tasks.length} total</span>
            </div>

            <div className="task-toolbar">
              <div className="search-box">
                <span aria-hidden="true">⌕</span>
                <input
                  aria-label="Search tasks"
                  placeholder="Search tasks..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>
              <select
                aria-label="Filter by status"
                value={filter}
                onChange={(event) => setFilter(event.target.value)}
              >
                <option>All</option>
                <option>Pending</option>
                <option>Completed</option>
              </select>
            </div>

            <div className="task-list">
              {filteredTasks.map((task) => (
                <article className="task-row" key={task.id}>
                  <button
                    className={`task-check ${task.status === "Completed" ? "checked" : ""}`}
                    type="button"
                    onClick={() => toggleTask(task.id)}
                    aria-label={task.status === "Completed" ? `Mark ${task.title} pending` : `Mark ${task.title} completed`}
                    aria-pressed={task.status === "Completed"}
                  >
                    {task.status === "Completed" ? "✓" : ""}
                  </button>
                  <div className="task-main">
                    <h3 className={task.status === "Completed" ? "done-title" : ""}>
                      {task.title}
                    </h3>
                    {task.description && <p>{task.description}</p>}
                    <p>
                      {task.category}
                      {task.evidence && <> · <span className="evidence">{task.evidence}</span></>}
                    </p>
                    {task.conflict && (
                      <p className="warning-text task-warning">⚠ Potential deadline conflict — verify the original messages.</p>
                    )}
                    {task.warnings.length > 0 && (
                      <details className="task-warnings">
                        <summary>{task.warnings.length} warning{task.warnings.length === 1 ? "" : "s"}</summary>
                        <ul>{task.warnings.map((warning, index) => <li key={`${task.id}-warning-${index}`}>{warning}</li>)}</ul>
                      </details>
                    )}
                  </div>
                  <span className={`priority priority-${task.priority.toLowerCase()}`}>
                    {task.priority}
                  </span>
                  <div className="task-deadline">
                    <span>DEADLINE</span>
                    <strong>{formatDeadline(task)}</strong>
                    {task.urgency && <small>{task.urgency}</small>}
                  </div>
                </article>
              ))}
              {filteredTasks.length === 0 && (
                <div className="empty-state">
                  {tasks.length === 0
                    ? "No tasks loaded yet. Import a WhatsApp export ZIP to get started."
                    : activeNav === "Conflicts"
                      ? "No potential conflicts found in the current task list."
                      : "No matching tasks found. Try changing your search or filter."}
                </div>
              )}
            </div>
          </section>

          <footer>CampusPilot · Built to make campus life easier.</footer>
        </section>
      </main>
    </div>
  );
}

function StatCard({ label, value, note, icon }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <span className="stat-icon" aria-hidden="true">{icon}</span>
      </div>
      <strong className="stat-value">{value}</strong>
      <span className="stat-note">{note}</span>
    </article>
  );
}

export default App;
