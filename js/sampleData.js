// sampleData.js - Default data to make CozyStudy immediately vibrant and functional

export const INITIAL_SUBJECTS = [
  { id: 'cs101', name: 'Data Structures & Algorithms', code: 'CS 201', color: '#88B04B', icon: '💻' },
  { id: 'math', name: 'Linear Algebra & Calculus', code: 'MATH 150', color: '#92A8D1', icon: '📐' },
  { id: 'bio', name: 'Molecular Biology', code: 'BIO 110', color: '#F7CAC9', icon: '🧬' },
  { id: 'lit', name: 'World Literature & Essay', code: 'LIT 102', color: '#E0BBE4', icon: '📖' },
  { id: 'art', name: 'Digital Art & Design', code: 'ART 210', color: '#FFD3B6', icon: '🎨' }
];

export const INITIAL_CHARMS = [
  // Starter unlocked charms
  { id: 'charm_matcha', name: 'Steaming Matcha Latte', category: 'desk', icon: '🍵', cost: 0, unlocked: true, equipped: true, description: 'Warm ceramic mug of whisked ceremonial matcha' },
  { id: 'charm_lamp', name: 'Pastel Desk Lamp', category: 'desk', icon: '🛋️', cost: 0, unlocked: true, equipped: true, description: 'Soft warm glow for late-night focus' },
  { id: 'charm_calico', name: 'Sleeping Calico Cat (Mochi)', category: 'pet', icon: '🐱', cost: 0, unlocked: true, equipped: true, description: 'Purrs quietly when your focus integrity is high' },
  { id: 'charm_succulent', name: 'Baby Succulent Pot', category: 'desk', icon: '🪴', cost: 30, unlocked: true, equipped: true, description: 'Thrives on your steady study consistency' },
  { id: 'charm_fairylights', name: 'Cozy Fairy Lights', category: 'wall', icon: '✨', cost: 50, unlocked: true, equipped: true, description: 'Twinkles along the window frame' },
  
  // Unlockable charms
  { id: 'charm_radio', name: 'Vintage Lo-Fi Cassette Radio', category: 'desk', icon: '📻', cost: 75, unlocked: false, equipped: false, description: 'Plays imagined lo-fi beats from rainy afternoons' },
  { id: 'charm_bunny', name: 'Fluffy Mochi Bunny', category: 'pet', icon: '🐰', cost: 90, unlocked: false, equipped: false, description: 'Hops onto the rug during break time' },
  { id: 'charm_crystal', name: 'Amethyst Focus Crystal', category: 'desk', icon: '🔮', cost: 120, unlocked: false, equipped: false, description: 'Radiates calm and dispels tab-switching urges' },
  { id: 'charm_polaroids', name: 'Polaroid Memory Wall', category: 'wall', icon: '📸', cost: 80, unlocked: false, equipped: false, description: 'Snapshots of finished goals and coffee dates' },
  { id: 'charm_monstera', name: 'Giant Monstera Deliciosa', category: 'floor', icon: '🌿', cost: 100, unlocked: false, equipped: false, description: 'Lush green companion standing tall in the corner' },
  { id: 'charm_beanbag', name: 'Velvet Cloud Beanbag', category: 'floor', icon: '☁️', cost: 110, unlocked: false, equipped: false, description: 'The coziest reading spot in the whole room' },
  { id: 'charm_globe', name: 'Floating Celestial Moon Globe', category: 'desk', icon: '🌙', cost: 160, unlocked: false, equipped: false, description: 'Glows in synchrony with lunar study cycles' },
  { id: 'charm_clock', name: 'Cuckoo Studio Clock', category: 'wall', icon: '🕰️', cost: 130, unlocked: false, equipped: false, description: 'Ticking rhythm of undisturbed productivity' },
  { id: 'charm_tea_set', name: 'Floral Sakura Tea Set', category: 'desk', icon: '🫖', cost: 95, unlocked: false, equipped: false, description: 'Fragrant jasmine tea with delicate porcelain cups' }
];

export const INITIAL_TASKS = [
  {
    id: 'task-1',
    title: 'Complete Red-Black Tree Implementation',
    subjectId: 'cs101',
    priority: 'high',
    dueDate: new Date(Date.now() + 86400000 * 2).toISOString().slice(0, 10), // in 2 days
    estimatedCycles: 3,
    completedCycles: 1,
    status: 'in_progress',
    createdAt: new Date(Date.now() - 86400000 * 1).toISOString(),
    notes: 'Implement left-rotate, right-rotate, and re-balancing insertions.'
  },
  {
    id: 'task-2',
    title: 'Calculus Problem Set 4 (Eigenvalues)',
    subjectId: 'math',
    priority: 'high',
    dueDate: new Date(Date.now() + 86400000 * 1).toISOString().slice(0, 10), // tomorrow
    estimatedCycles: 2,
    completedCycles: 0,
    status: 'todo',
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    notes: 'Odd-numbered problems from Chapter 5.3.'
  },
  {
    id: 'task-3',
    title: 'Literature Synthesis Essay: Modernism',
    subjectId: 'lit',
    priority: 'medium',
    dueDate: new Date(Date.now() + 86400000 * 5).toISOString().slice(0, 10),
    estimatedCycles: 4,
    completedCycles: 2,
    status: 'in_progress',
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
    notes: 'Draft 1,500 words comparing Woolf and Joyce.'
  },
  {
    id: 'task-4',
    title: 'Review Cellular Respiration Diagrams',
    subjectId: 'bio',
    priority: 'low',
    dueDate: new Date(Date.now() + 86400000 * 7).toISOString().slice(0, 10),
    estimatedCycles: 1,
    completedCycles: 1,
    status: 'completed',
    completedAt: new Date(Date.now() - 3600000 * 4).toISOString(),
    createdAt: new Date(Date.now() - 86400000 * 4).toISOString(),
    notes: 'Memorize Krebs cycle enzymes and ATP outputs.'
  },
  {
    id: 'task-5',
    title: 'Character Color Palette & Moodboard',
    subjectId: 'art',
    priority: 'medium',
    dueDate: new Date(Date.now() + 86400000 * 4).toISOString().slice(0, 10),
    estimatedCycles: 2,
    completedCycles: 0,
    status: 'todo',
    createdAt: new Date(Date.now() - 86400000 * 1).toISOString(),
    notes: 'Select 5 pastel color swatches for the cozy diorama project.'
  }
];

export const INITIAL_SESSIONS = [
  // Realistic sessions from today and past couple days to populate focus graphs
  {
    id: 'sess-1',
    taskId: 'task-1',
    taskTitle: 'Complete Red-Black Tree Implementation',
    subjectId: 'cs101',
    startTime: new Date(Date.now() - 7200000).toISOString(),
    durationSeconds: 1500, // 25 min
    activeFocusSeconds: 1420, // 94.6% focus
    distractedSeconds: 80,
    tabSwitches: 2,
    integrityRate: 95,
    mode: 'honest',
    completed: true,
    charmsEarned: 15
  },
  {
    id: 'sess-2',
    taskId: 'task-3',
    taskTitle: 'Literature Synthesis Essay: Modernism',
    subjectId: 'lit',
    startTime: new Date(Date.now() - 14400000).toISOString(),
    durationSeconds: 1500,
    activeFocusSeconds: 1310, // 87.3%
    distractedSeconds: 190,
    tabSwitches: 4,
    integrityRate: 87,
    mode: 'honest',
    completed: true,
    charmsEarned: 12
  },
  {
    id: 'sess-3',
    taskId: 'task-4',
    taskTitle: 'Review Cellular Respiration Diagrams',
    subjectId: 'bio',
    startTime: new Date(Date.now() - 86400000 * 1 - 3600000 * 5).toISOString(),
    durationSeconds: 1500,
    activeFocusSeconds: 1480, // 98.6%
    distractedSeconds: 20,
    tabSwitches: 1,
    integrityRate: 99,
    mode: 'honest',
    completed: true,
    charmsEarned: 20
  },
  {
    id: 'sess-4',
    taskId: 'task-1',
    taskTitle: 'Complete Red-Black Tree Implementation',
    subjectId: 'cs101',
    startTime: new Date(Date.now() - 86400000 * 1 - 3600000 * 2).toISOString(),
    durationSeconds: 1500,
    activeFocusSeconds: 1100, // 73.3% - slight distraction
    distractedSeconds: 400,
    tabSwitches: 7,
    integrityRate: 73,
    mode: 'honest',
    completed: true,
    charmsEarned: 6
  },
  {
    id: 'sess-5',
    taskId: 'task-3',
    taskTitle: 'Literature Synthesis Essay: Modernism',
    subjectId: 'lit',
    startTime: new Date(Date.now() - 86400000 * 2 - 3600000 * 3).toISOString(),
    durationSeconds: 1800, // 30 min
    activeFocusSeconds: 1710,
    distractedSeconds: 90,
    tabSwitches: 2,
    integrityRate: 95,
    mode: 'honest',
    completed: true,
    charmsEarned: 18
  },
  {
    id: 'sess-6',
    taskId: null,
    taskTitle: 'General Deep Study & Code Warmup',
    subjectId: 'cs101',
    startTime: new Date(Date.now() - 86400000 * 3 - 3600000 * 4).toISOString(),
    durationSeconds: 1500,
    activeFocusSeconds: 1450,
    distractedSeconds: 50,
    tabSwitches: 1,
    integrityRate: 97,
    mode: 'honest',
    completed: true,
    charmsEarned: 15
  }
];
