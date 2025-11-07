import { useState, useEffect } from 'react';
import { 
  CheckCircle, Circle, Plus, Trash2, LogOut, BarChart3, 
  Filter, RefreshCw, User, Lock, Server 
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '/api';

export default function App() {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [ssoStatus, setSsoStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Forms
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [taskForm, setTaskForm] = useState({ 
    title: '', 
    description: '', 
    priority: 'medium', 
    status: 'todo' 
  });
  
  // Filters & UI
  const [filter, setFilter] = useState({ status: 'all', priority: 'all' });
  const [showStats, setShowStats] = useState(false);

  // Fetch SSO status
  const fetchSsoStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/sso-status`);
      if (response.ok) {
        const data = await response.json();
        setSsoStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch SSO status:', err);
    }
  };

  // Login
  const login = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('auth_type', data.auth_type || 'local');
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        setUser(data.user);
        fetchTasks(data.access_token);
        fetchStats(data.access_token);
      } else {
        const err = await response.json();
        setError(err.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      });
    } catch (err) {
      console.error('Logout error:', err);
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('auth_type');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setTasks([]);
    setStats(null);
  };

  // Fetch tasks
  const fetchTasks = async (token = localStorage.getItem('token')) => {
    try {
      const response = await fetch(`${API_URL}/tasks`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      } else if (response.status === 401) {
        logout();
      }
    } catch (err) {
      console.error('Fetch tasks error:', err);
    }
  };

  // Fetch stats
  const fetchStats = async (token = localStorage.getItem('token')) => {
    try {
      const response = await fetch(`${API_URL}/stats`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Fetch stats error:', err);
    }
  };

  // Create task
  const createTask = async (e) => {
    e.preventDefault();
    if (!taskForm.title.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(taskForm),
      });
      
      if (response.ok) {
        setTaskForm({ title: '', description: '', priority: 'medium', status: 'todo' });
        fetchTasks();
        fetchStats();
      } else if (response.status === 401) {
        logout();
      }
    } catch (err) {
      console.error('Create task error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Toggle task status
  const toggleTask = async (taskId, currentStatus) => {
    const newStatus = currentStatus === 'done' ? 'todo' : 'done';
    const newCompleted = newStatus === 'done';
    
    try {
      const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ 
          status: newStatus,
          completed: newCompleted 
        }),
      });
      
      if (response.ok) {
        fetchTasks();
        fetchStats();
      } else if (response.status === 401) {
        logout();
      }
    } catch (err) {
      console.error('Toggle task error:', err);
    }
  };

  // Delete task
  const deleteTask = async (taskId) => {
    if (!confirm('Delete this task?')) return;
    
    try {
      const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      });
      
      if (response.ok) {
        fetchTasks();
        fetchStats();
      } else if (response.status === 401) {
        logout();
      }
    } catch (err) {
      console.error('Delete task error:', err);
    }
  };

  // Filter tasks
  const filteredTasks = tasks.filter(task => {
    if (filter.status !== 'all' && task.status !== filter.status) return false;
    if (filter.priority !== 'all' && task.priority !== filter.priority) return false;
    return true;
  });

  // Check token on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    fetchSsoStatus();
    
    if (token) {
      fetch(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` },
      })
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            setUser(data);
            fetchTasks(token);
            fetchStats(token);
          } else {
            logout();
          }
        })
        .catch(() => logout());
    }
  }, []);

  // Priority colors
  const priorityColors = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800',
  };

  const statusColors = {
    todo: 'bg-gray-100 text-gray-800',
    in_progress: 'bg-blue-100 text-blue-800',
    review: 'bg-purple-100 text-purple-800',
    done: 'bg-green-100 text-green-800',
    archived: 'bg-gray-200 text-gray-600',
  };

  // Login screen
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="text-white" size={32} />
            </div>
            <h1 className="text-3xl font-bold text-gray-800">Task Manager Pro</h1>
            <p className="text-gray-600 mt-2">Sign in to continue</p>
            
            {ssoStatus && ssoStatus.sso_enabled && (
              <div className="mt-4 flex items-center justify-center gap-2 text-sm text-green-600">
                <Server size={16} />
                <span>SSO Enabled ({ssoStatus.keycloak_realm})</span>
              </div>
            )}
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
          
          <form onSubmit={login} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User size={16} className="inline mr-2" />
                Username
              </label>
              <input
                type="text"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter username"
                required
                autoFocus
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Lock size={16} className="inline mr-2" />
                Password
              </label>
              <input
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter password"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <RefreshCw className="animate-spin mr-2" size={18} />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
          
          <div className="mt-6 text-center text-xs text-gray-500">
            <p>Credentials from Vault • {ssoStatus?.sso_enabled ? 'Keycloak SSO' : 'Local Auth'}</p>
          </div>
        </div>
      </div>
    );
  }

  // Main app
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 w-10 h-10 rounded-lg flex items-center justify-center">
                <CheckCircle className="text-white" size={20} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Task Manager Pro</h1>
                <p className="text-sm text-gray-600">
                  Hello, {user.full_name || user.username}! 
                  {user.is_admin && <span className="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded">Admin</span>}
                  <span className="ml-2 text-xs text-gray-500">
                    ({localStorage.getItem('auth_type') === 'keycloak' ? '🔐 SSO' : '🔑 Local'})
                  </span>
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowStats(!showStats)}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <BarChart3 size={18} />
                <span>Stats</span>
              </button>
              
              <button
                onClick={logout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics */}
        {showStats && stats && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6 animate-fade-in">
            <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">{stats.total_tasks}</div>
                <div className="text-sm text-gray-600">Total Tasks</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">{stats.completed_tasks}</div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-yellow-600">{stats.active_tasks}</div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">
                  {stats.total_tasks ? Math.round((stats.completed_tasks / stats.total_tasks) * 100) : 0}%
                </div>
                <div className="text-sm text-gray-600">Progress</div>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Create Task Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-800 mb-4">➕ New Task</h2>
              
              <form onSubmit={createTask} className="space-y-4">
                <input
                  type="text"
                  value={taskForm.title}
                  onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
                  placeholder="Task title"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                
                <textarea
                  value={taskForm.description}
                  onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                  placeholder="Description (optional)"
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                
                <div className="grid grid-cols-2 gap-3">
                  <select
                    value={taskForm.priority}
                    onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
                    className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">🔵 Low</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="high">🟠 High</option>
                    <option value="urgent">🔴 Urgent</option>
                  </select>
                  
                  <select
                    value={taskForm.status}
                    onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}
                    className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="review">Review</option>
                    <option value="done">Done</option>
                  </select>
                </div>
                
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <Plus size={20} />
                  <span>{loading ? 'Creating...' : 'Create Task'}</span>
                </button>
              </form>
            </div>
          </div>

          {/* Tasks List */}
          <div className="lg:col-span-2">
            {/* Filters */}
            <div className="bg-white rounded-xl shadow-lg p-4 mb-6">
              <div className="flex items-center space-x-4">
                <Filter size={20} className="text-gray-600" />
                <select
                  value={filter.status}
                  onChange={(e) => setFilter({ ...filter, status: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Statuses</option>
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="review">Review</option>
                  <option value="done">Done</option>
                </select>
                
                <select
                  value={filter.priority}
                  onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Priorities</option>
                  <option value="urgent">🔴 Urgent</option>
                  <option value="high">🟠 High</option>
                  <option value="medium">🟡 Medium</option>
                  <option value="low">🔵 Low</option>
                </select>
              </div>
            </div>

            {/* Tasks */}
            <div className="space-y-3">
              {filteredTasks.length === 0 ? (
                <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                  <Circle size={48} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-600">No tasks yet</p>
                  <p className="text-sm text-gray-500 mt-2">Create your first task to get started!</p>
                </div>
              ) : (
                filteredTasks.map((task) => (
                  <div
                    key={task.id}
                    className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <button
                          onClick={() => toggleTask(task.id, task.status)}
                          className="mt-1 flex-shrink-0"
                        >
                          {task.status === 'done' ? (
                            <CheckCircle size={24} className="text-green-600" />
                          ) : (
                            <Circle size={24} className="text-gray-400 hover:text-blue-600 transition-colors" />
                          )}
                        </button>
                        
                        <div className="flex-1">
                          <h3 className={`text-lg font-semibold ${task.status === 'done' ? 'line-through text-gray-400' : 'text-gray-800'}`}>
                            {task.title}
                          </h3>
                          {task.description && (
                            <p className="text-gray-600 mt-1 text-sm">{task.description}</p>
                          )}
                          <div className="flex items-center space-x-2 mt-3">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${priorityColors[task.priority]}`}>
                              {task.priority}
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[task.status]}`}>
                              {task.status.replace('_', ' ')}
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(task.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}