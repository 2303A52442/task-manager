import { useEffect, useMemo, useState } from 'react';

const API_BASE = '/api';

async function apiRequest(path, options = {}) {
  const init = {
    credentials: 'same-origin',
    ...options,
  };

  if (init.body && typeof init.body !== 'string') {
    init.headers = {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    };
    init.body = JSON.stringify(init.body);
  }

  const response = await fetch(`${API_BASE}${path}`, init);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.message || 'Request failed.');
  }

  return payload;
}

function formatDateLabel(value) {
  if (!value) {
    return { month: '---', day: '--', year: '----' };
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return { month: '---', day: '--', year: '----' };
  }

  return {
    month: parsed.toLocaleString('en-US', { month: 'short' }).toUpperCase(),
    day: String(parsed.getDate()).padStart(2, '0'),
    year: String(parsed.getFullYear()),
  };
}

function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [auth, setAuth] = useState({ authenticated: false, username: null });
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname);
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (nextPath, replace = false) => {
    if (replace) {
      window.history.replaceState({}, '', nextPath);
    } else {
      window.history.pushState({}, '', nextPath);
    }
    setPath(nextPath);
  };

  const loadSession = async () => {
    setLoading(true);
    setError('');

    try {
      const me = await apiRequest('/me');
      setAuth(me);

      if (me.authenticated) {
        const taskResponse = await apiRequest('/tasks');
        setTasks(taskResponse.tasks || []);

        if (path === '/login' || path === '/register') {
          navigate('/', true);
        }
      } else {
        setTasks([]);
        if (path === '/') {
          navigate('/login', true);
        }
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
  }, []);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (!auth.authenticated && path === '/') {
      navigate('/login', true);
    }

    if (auth.authenticated && (path === '/login' || path === '/register')) {
      navigate('/', true);
    }
  }, [auth.authenticated, loading, path]);

  const refreshTasks = async () => {
    const taskResponse = await apiRequest('/tasks');
    setTasks(taskResponse.tasks || []);
  };

  const handleAuth = async (route, credentials, successMessage) => {
    setBusy(true);
    setError('');
    setNotice('');

    try {
      await apiRequest(route, {
        method: 'POST',
        body: credentials,
      });

      setNotice(successMessage);

      if (route === '/login') {
        const me = await apiRequest('/me');
        setAuth(me);
        const taskResponse = await apiRequest('/tasks');
        setTasks(taskResponse.tasks || []);
        navigate('/', true);
      } else {
        navigate('/login', true);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const handleLogout = async () => {
    setBusy(true);
    setError('');

    try {
      await apiRequest('/logout', { method: 'POST' });
      setAuth({ authenticated: false, username: null });
      setTasks([]);
      navigate('/login', true);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const handleTaskCreate = async (draft) => {
    setBusy(true);
    setError('');

    try {
      await apiRequest('/tasks', {
        method: 'POST',
        body: draft,
      });
      await refreshTasks();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const handleToggle = async (taskId) => {
    setBusy(true);
    setError('');

    try {
      await apiRequest(`/tasks/${taskId}/toggle`, { method: 'POST' });
      await refreshTasks();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async (taskId) => {
    setBusy(true);
    setError('');

    try {
      await apiRequest(`/tasks/${taskId}`, { method: 'DELETE' });
      await refreshTasks();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const completedCount = useMemo(
    () => tasks.filter((task) => task.done).length,
    [tasks],
  );

  const activeCount = tasks.length - completedCount;
  const completionRate = tasks.length ? Math.round((completedCount / tasks.length) * 100) : 0;

  if (loading) {
    return (
      <div className="app-shell">
        <div className="ambient ambient-a" />
        <div className="ambient ambient-b" />
        <main className="loading-screen">
          <p className="eyebrow">Task Forge</p>
          <h1>Loading your workspace</h1>
          <p className="muted">Preparing your tasks and session state.</p>
        </main>
      </div>
    );
  }

  const view = path === '/register' ? 'register' : path === '/login' ? 'login' : 'dashboard';

  return (
    <div className="app-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />

      {view === 'dashboard' ? (
        <Dashboard
          username={auth.username}
          tasks={tasks}
          completedCount={completedCount}
          activeCount={activeCount}
          completionRate={completionRate}
          busy={busy}
          error={error}
          notice={notice}
          onLogout={handleLogout}
          onAddTask={handleTaskCreate}
          onToggleTask={handleToggle}
          onDeleteTask={handleDelete}
        />
      ) : (
        <AuthScreen
          mode={view}
          busy={busy}
          error={error}
          notice={notice}
          onNavigate={navigate}
          onSubmit={(credentials) =>
            handleAuth(view === 'login' ? '/login' : '/register', credentials, view === 'login' ? 'Welcome back.' : 'Account created. You can log in now.')
          }
        />
      )}
    </div>
  );
}

function AuthScreen({ mode, busy, error, notice, onNavigate, onSubmit }) {
  const [form, setForm] = useState({ username: '', password: '' });

  const submitLabel = mode === 'login' ? 'Log in' : 'Create account';
  const headline = mode === 'login' ? 'Welcome back' : 'Build your account';
  const copy =
    mode === 'login'
      ? 'Pick up where you left off and keep your tasks moving.'
      : 'Create a new workspace for your daily planning flow.';

  return (
    <main className="auth-layout">
      <section className="hero-panel glass-panel">
        <p className="eyebrow">Task Forge</p>
        <h1>{headline}</h1>
        <p className="hero-copy">{copy}</p>

        <div className="signal-grid">
          <div>
            <span className="signal-value">React</span>
            <span className="signal-label">frontend</span>
          </div>
          <div>
            <span className="signal-value">Flask</span>
            <span className="signal-label">API layer</span>
          </div>
          <div>
            <span className="signal-value">Session</span>
            <span className="signal-label">auth state</span>
          </div>
        </div>
      </section>

      <section className="auth-panel glass-panel">
        <div className="panel-head">
          <p className="eyebrow">{mode === 'login' ? 'Sign in' : 'Register'}</p>
          <h2>{submitLabel}</h2>
        </div>

        {error ? <div className="banner banner-error">{error}</div> : null}
        {notice ? <div className="banner banner-success">{notice}</div> : null}

        <form
          className="stacked-form"
          onSubmit={(event) => {
            event.preventDefault();
            onSubmit(form);
          }}
        >
          <label>
            <span>Username</span>
            <input
              value={form.username}
              onChange={(event) => setForm({ ...form, username: event.target.value })}
              placeholder="Enter your username"
              autoComplete="username"
              required
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              placeholder="Enter your password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
            />
          </label>

          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? 'Working...' : submitLabel}
          </button>
        </form>

        <p className="auth-switch">
          {mode === 'login' ? 'Need an account?' : 'Already have an account?'}{' '}
          <button
            type="button"
            className="text-button"
            onClick={() => onNavigate(mode === 'login' ? '/register' : '/login')}
          >
            {mode === 'login' ? 'Register' : 'Log in'}
          </button>
        </p>
      </section>
    </main>
  );
}

function Dashboard({
  username,
  tasks,
  completedCount,
  activeCount,
  completionRate,
  busy,
  error,
  notice,
  onLogout,
  onAddTask,
  onToggleTask,
  onDeleteTask,
}) {
  return (
    <main className="dashboard-layout">
      <header className="topbar glass-panel">
        <div>
          <p className="eyebrow">Task Forge</p>
          <h1>Dashboard</h1>
          <p className="hero-copy">A cleaner way to track what matters today.</p>
        </div>

        <div className="topbar-actions">
          <div className="user-pill">{username}</div>
          <button className="secondary-button" onClick={onLogout} disabled={busy}>
            Log out
          </button>
        </div>
      </header>

      <section className="stats-grid">
        <article className="stat-card glass-panel">
          <span className="stat-label">Open tasks</span>
          <strong>{activeCount}</strong>
        </article>
        <article className="stat-card glass-panel">
          <span className="stat-label">Completed</span>
          <strong>{completedCount}</strong>
        </article>
        <article className="stat-card glass-panel">
          <span className="stat-label">Completion</span>
          <strong>{completionRate}%</strong>
        </article>
      </section>

      {error ? <div className="banner banner-error">{error}</div> : null}
      {notice ? <div className="banner banner-success">{notice}</div> : null}

      <section className="content-grid">
        <TaskComposer onAddTask={onAddTask} busy={busy} />
        <TaskList
          tasks={tasks}
          busy={busy}
          onToggleTask={onToggleTask}
          onDeleteTask={onDeleteTask}
        />
      </section>
    </main>
  );
}

function TaskComposer({ onAddTask, busy }) {
  const [draft, setDraft] = useState({ title: '', description: '' });

  return (
    <section className="glass-panel composer-panel">
      <div className="panel-head">
        <p className="eyebrow">New task</p>
        <h2>Capture the next move</h2>
      </div>

      <form
        className="stacked-form"
        onSubmit={async (event) => {
          event.preventDefault();
          await onAddTask(draft);
          setDraft({ title: '', description: '' });
        }}
      >
        <label>
          <span>Task title</span>
          <input
            value={draft.title}
            onChange={(event) => setDraft({ ...draft, title: event.target.value })}
            placeholder="Write the task title"
            required
          />
        </label>

        <label>
          <span>Description</span>
          <textarea
            value={draft.description}
            onChange={(event) => setDraft({ ...draft, description: event.target.value })}
            placeholder="Optional details, context, or next steps"
            rows="5"
          />
        </label>

        <button className="primary-button" type="submit" disabled={busy}>
          {busy ? 'Saving...' : 'Add task'}
        </button>
      </form>
    </section>
  );
}

function TaskList({ tasks, busy, onToggleTask, onDeleteTask }) {
  return (
    <section className="glass-panel tasks-panel">
      <div className="panel-head panel-head-row">
        <div>
          <p className="eyebrow">Task list</p>
          <h2>Your queue</h2>
        </div>
        <div className="count-chip">
          {tasks.length} task{tasks.length === 1 ? '' : 's'}
        </div>
      </div>

      {tasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">◌</div>
          <h3>No tasks yet</h3>
          <p>Add your first task on the left to start building momentum.</p>
        </div>
      ) : (
        <div className="task-stack">
          {tasks.map((task) => {
            const date = formatDateLabel(task.created_at);

            return (
              <article key={task.id} className={`task-card ${task.done ? 'done' : ''}`}>
                <div className="task-date">
                  <span>{date.month}</span>
                  <strong>{date.day}</strong>
                  <small>{date.year}</small>
                </div>

                <div className="task-body">
                  <div className="task-copy">
                    <h3>{task.title}</h3>
                    {task.description ? <p>{task.description}</p> : null}
                  </div>

                  <div className="task-actions">
                    <button className="secondary-button" onClick={() => onToggleTask(task.id)} disabled={busy}>
                      {task.done ? 'Undo' : 'Done'}
                    </button>
                    <button className="danger-button" onClick={() => onDeleteTask(task.id)} disabled={busy}>
                      Delete
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default App;