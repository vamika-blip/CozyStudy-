// state.js - Central Reactive State Store for CozyStudy
import { INITIAL_SUBJECTS, INITIAL_CHARMS, INITIAL_TASKS, INITIAL_SESSIONS } from './sampleData.js';

const STORAGE_KEY = 'cozystudy_state_v1';

class Store {
  constructor() {
    this.listeners = new Set();
    this.state = this.loadState();
  }

  getDefaultState() {
    return {
      coins: 85, // Starting Star Charms ✨
      subjects: INITIAL_SUBJECTS,
      charms: INITIAL_CHARMS,
      tasks: INITIAL_TASKS,
      sessions: INITIAL_SESSIONS,
      activeTaskId: null,
      settings: {
        theme: 'sakura', // sakura | matcha | lavender | midnight
        antiCheatMode: 'honest', // honest | strict
        ambientSound: 'none', // none | rain | cafe | fire
        ambientVolume: 0.5,
        pomodoroMinutes: 25,
        shortBreakMinutes: 5,
        longBreakMinutes: 15,
        autoStartBreaks: false,
        soundEnabled: true
      },
      stats: {
        currentStreak: 3,
        bestStreak: 7,
        lastActiveDate: new Date().toISOString().slice(0, 10)
      }
    };
  }

  loadState() {
    try {
      const serialized = localStorage.getItem(STORAGE_KEY);
      if (!serialized) {
        return this.getDefaultState();
      }
      const parsed = JSON.parse(serialized);
      // Defensive merging to guarantee fields exist
      const defaults = this.getDefaultState();
      return {
        ...defaults,
        ...parsed,
        subjects: Array.isArray(parsed.subjects) && parsed.subjects.length > 0 ? parsed.subjects : defaults.subjects,
        charms: Array.isArray(parsed.charms) && parsed.charms.length > 0 ? parsed.charms : defaults.charms,
        tasks: Array.isArray(parsed.tasks) ? parsed.tasks : defaults.tasks,
        sessions: Array.isArray(parsed.sessions) ? parsed.sessions : defaults.sessions,
        settings: { ...defaults.settings, ...(parsed.settings || {}) },
        stats: { ...defaults.stats, ...(parsed.stats || {}) }
      };
    } catch (err) {
      console.warn('Failed to parse localStorage, resetting to default state:', err);
      return this.getDefaultState();
    }
  }

  saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
    } catch (err) {
      console.error('Failed to save state to localStorage:', err);
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify(changeType, payload) {
    this.saveState();
    for (const listener of this.listeners) {
      try {
        listener(this.state, changeType, payload);
      } catch (err) {
        console.error('Store listener error:', err);
      }
    }
  }

  // --- Coin / Charm Actions ---
  addCoins(amount, reason = '') {
    this.state.coins = Math.max(0, (this.state.coins || 0) + amount);
    this.notify('COINS_UPDATED', { amount, reason });
  }

  unlockCharm(charmId) {
    const charm = this.state.charms.find(c => c.id === charmId);
    if (!charm) return false;
    if (charm.unlocked) return true;
    if (this.state.coins < charm.cost) return false;

    this.state.coins -= charm.cost;
    charm.unlocked = true;
    charm.equipped = true;
    this.notify('CHARM_UNLOCKED', { charm });
    return true;
  }

  toggleEquipCharm(charmId) {
    const charm = this.state.charms.find(c => c.id === charmId);
    if (!charm || !charm.unlocked) return false;

    charm.equipped = !charm.equipped;
    this.notify('CHARM_EQUIPPED', { charm });
    return true;
  }

  // --- Task Actions ---
  addTask(taskData) {
    const newTask = {
      id: 'task_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
      title: taskData.title.trim(),
      subjectId: taskData.subjectId || 'cs101',
      priority: taskData.priority || 'medium',
      dueDate: taskData.dueDate || new Date().toISOString().slice(0, 10),
      estimatedCycles: parseInt(taskData.estimatedCycles, 10) || 1,
      completedCycles: 0,
      status: 'todo',
      notes: taskData.notes || '',
      createdAt: new Date().toISOString()
    };
    this.state.tasks.unshift(newTask);
    this.notify('TASK_ADDED', { task: newTask });
    return newTask;
  }

  updateTask(taskId, updates) {
    const task = this.state.tasks.find(t => t.id === taskId);
    if (!task) return null;

    Object.assign(task, updates);
    this.notify('TASK_UPDATED', { task });
    return task;
  }

  deleteTask(taskId) {
    this.state.tasks = this.state.tasks.filter(t => t.id !== taskId);
    if (this.state.activeTaskId === taskId) {
      this.state.activeTaskId = null;
    }
    this.notify('TASK_DELETED', { taskId });
  }

  setActiveTask(taskId) {
    this.state.activeTaskId = taskId;
    this.notify('ACTIVE_TASK_CHANGED', { taskId });
  }

  completeTask(taskId) {
    const task = this.state.tasks.find(t => t.id === taskId);
    if (!task) return;

    task.status = 'completed';
    task.completedAt = new Date().toISOString();

    // Reward calculation: Bonus coins for finishing on time
    let reward = 20;
    const nowStr = new Date().toISOString().slice(0, 10);
    if (task.dueDate && task.dueDate >= nowStr) {
      reward += 15; // On-time / early bonus!
    }
    if (task.priority === 'high') {
      reward += 10;
    }
    this.addCoins(reward, `Completed task: ${task.title}`);
    this.notify('TASK_COMPLETED', { task, reward });
  }

  // --- Session Logging ---
  addSession(sessionData) {
    const newSession = {
      id: 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
      ...sessionData,
      createdAt: new Date().toISOString()
    };
    this.state.sessions.unshift(newSession);

    // If bound to a task, increment task completed cycles
    if (newSession.taskId) {
      const task = this.state.tasks.find(t => t.id === newSession.taskId);
      if (task) {
        task.completedCycles = (task.completedCycles || 0) + 1;
        if (task.status === 'todo') {
          task.status = 'in_progress';
        }
      }
    }

    // Update daily streak
    this.updateStreak();

    // Award charms coins based on focus integrity!
    if (newSession.charmsEarned > 0) {
      this.addCoins(newSession.charmsEarned, `Focus session (${newSession.integrityRate}% integrity)`);
    }

    this.notify('SESSION_LOGGED', { session: newSession });
    return newSession;
  }

  updateStreak() {
    const todayStr = new Date().toISOString().slice(0, 10);
    const lastActive = this.state.stats.lastActiveDate;

    if (lastActive !== todayStr) {
      const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      if (lastActive === yesterday) {
        this.state.stats.currentStreak += 1;
      } else {
        this.state.stats.currentStreak = 1;
      }
      if (this.state.stats.currentStreak > (this.state.stats.bestStreak || 1)) {
        this.state.stats.bestStreak = this.state.stats.currentStreak;
      }
      this.state.stats.lastActiveDate = todayStr;
    }
  }

  // --- Settings Actions ---
  updateSettings(partialSettings) {
    this.state.settings = {
      ...this.state.settings,
      ...partialSettings
    };
    this.notify('SETTINGS_UPDATED', { settings: this.state.settings });
  }

  // --- Backup & Restore ---
  exportJSON() {
    return JSON.stringify(this.state, null, 2);
  }

  importJSON(jsonString) {
    try {
      const parsed = JSON.parse(jsonString);
      if (parsed && typeof parsed === 'object') {
        this.state = {
          ...this.getDefaultState(),
          ...parsed
        };
        this.saveState();
        this.notify('STATE_IMPORTED', {});
        return true;
      }
    } catch (e) {
      console.error('Invalid backup JSON:', e);
    }
    return false;
  }

  resetToDemo() {
    this.state = this.getDefaultState();
    this.saveState();
    this.notify('STATE_RESET', {});
  }
}

export const store = new Store();
