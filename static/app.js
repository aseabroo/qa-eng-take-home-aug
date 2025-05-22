let currentPage = 0;
let currentFilters = {};
let allTasks = [];

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadTasks();
    loadProjects();
    loadUsers();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('createTaskForm').addEventListener('submit', handleCreateTask);
}

async function loadStats() {
    try {
        const [usersResponse, projectsResponse, tasksResponse] = await Promise.all([
            fetch('/api/v1/users/'),
            fetch('/api/v1/projects/'),
            fetch('/api/v1/tasks/')
        ]);

        const users = await usersResponse.json();
        const projects = await projectsResponse.json();
        const tasks = await tasksResponse.json();

        const todoTasks = tasks.filter(t => t.status === 'todo').length;
        const inProgressTasks = tasks.filter(t => t.status === 'in_progress').length;
        const doneTasks = tasks.filter(t => t.status === 'done').length;

        document.getElementById('stats-container').innerHTML = `
            <div class="row text-center">
                <div class="col">
                    <h4>${users.length}</h4>
                    <small class="text-muted">Users</small>
                </div>
                <div class="col">
                    <h4>${projects.length}</h4>
                    <small class="text-muted">Projects</small>
                </div>
                <div class="col">
                    <h4>${tasks.length}</h4>
                    <small class="text-muted">Tasks</small>
                </div>
            </div>
            <hr>
            <div class="row text-center">
                <div class="col">
                    <span class="badge bg-secondary">${todoTasks} To Do</span>
                </div>
                <div class="col">
                    <span class="badge bg-warning">${inProgressTasks} In Progress</span>
                </div>
                <div class="col">
                    <span class="badge bg-success">${doneTasks} Done</span>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('stats-container').innerHTML = '<p class="text-danger">Error loading stats</p>';
    }
}

async function loadTasks(reset = true) {
    if (reset) {
        currentPage = 0;
        allTasks = [];
    }

    try {
        const params = new URLSearchParams({
            skip: currentPage * 10,
            limit: 10,
            ...currentFilters
        });

        const response = await fetch(`/api/v1/tasks/?${params}`);
        const tasks = await response.json();

        if (reset) {
            allTasks = tasks;
        } else {
            allTasks = [...allTasks, ...tasks];
        }

        renderTasks();
        
        document.getElementById('loadMoreBtn').style.display = tasks.length === 10 ? 'block' : 'none';
        currentPage++;
    } catch (error) {
        console.error('Error loading tasks:', error);
        document.getElementById('tasks-container').innerHTML = '<p class="text-danger">Error loading tasks</p>';
    }
}

function renderTasks() {
    const container = document.getElementById('tasks-container');
    
    if (allTasks.length === 0) {
        container.innerHTML = '<p class="text-muted">No tasks found</p>';
        return;
    }

    container.innerHTML = allTasks.map(task => `
        <div class="card task-card mb-3 priority-${task.priority} status-${task.status}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title">${task.title}</h6>
                        <p class="card-text text-muted small">${task.description || 'No description'}</p>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${getPriorityColor(task.priority)}">${task.priority}</span>
                        <br>
                        <span class="badge bg-${getStatusColor(task.status)} mt-1">${task.status.replace('_', ' ')}</span>
                    </div>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <small class="text-muted">Project ID: ${task.project_id}</small>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="editTask(${task.id})">Edit</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function getPriorityColor(priority) {
    const colors = { high: 'danger', medium: 'warning', low: 'success' };
    return colors[priority] || 'secondary';
}

function getStatusColor(status) {
    const colors = { todo: 'secondary', in_progress: 'warning', done: 'success' };
    return colors[status] || 'secondary';
}

async function loadProjects() {
    try {
        const response = await fetch('/api/v1/projects/');
        const projects = await response.json();

        const container = document.getElementById('projects-container');
        container.innerHTML = projects.map(project => `
            <div class="card mb-2">
                <div class="card-body py-2">
                    <h6 class="card-title mb-1">${project.name}</h6>
                    <p class="card-text small text-muted">${project.description || 'No description'}</p>
                    <small class="text-muted">Owner ID: ${project.owner_id}</small>
                </div>
            </div>
        `).join('');

        // Populate project dropdown in modal
        const projectSelect = document.getElementById('taskProject');
        projectSelect.innerHTML = '<option value="">Select a project</option>' +
            projects.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading projects:', error);
        document.getElementById('projects-container').innerHTML = '<p class="text-danger">Error loading projects</p>';
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/v1/users/');
        const users = await response.json();

        const container = document.getElementById('users-container');
        container.innerHTML = users.map(user => `
            <div class="card mb-2">
                <div class="card-body py-2">
                    <h6 class="card-title mb-1">${user.name}</h6>
                    <p class="card-text small">${user.email}</p>
                    <span class="badge bg-${user.role === 'admin' ? 'primary' : 'secondary'}">${user.role}</span>
                </div>
            </div>
        `).join('');

        // Populate assignee dropdown in modal
        const assigneeSelect = document.getElementById('taskAssignee');
        assigneeSelect.innerHTML = '<option value="">Unassigned</option>' +
            users.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('users-container').innerHTML = '<p class="text-danger">Error loading users</p>';
    }
}

function filterTasks() {
    const status = document.getElementById('statusFilter').value;
    const priority = document.getElementById('priorityFilter').value;

    currentFilters = {};
    if (status) currentFilters.status_filter = status;
    if (priority) currentFilters.priority_filter = priority;

    loadTasks(true);
}

function searchTasks() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (searchTerm === '') {
        renderTasks();
        return;
    }

    const filteredTasks = allTasks.filter(task => 
        task.title.toLowerCase().includes(searchTerm) ||
        (task.description && task.description.toLowerCase().includes(searchTerm))
    );

    const container = document.getElementById('tasks-container');
    if (filteredTasks.length === 0) {
        container.innerHTML = '<p class="text-muted">No tasks match your search</p>';
        return;
    }

    container.innerHTML = filteredTasks.map(task => `
        <div class="card task-card mb-3 priority-${task.priority} status-${task.status}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title">${task.title}</h6>
                        <p class="card-text text-muted small">${task.description || 'No description'}</p>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${getPriorityColor(task.priority)}">${task.priority}</span>
                        <br>
                        <span class="badge bg-${getStatusColor(task.status)} mt-1">${task.status.replace('_', ' ')}</span>
                    </div>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <small class="text-muted">Project ID: ${task.project_id}</small>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="editTask(${task.id})">Edit</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function loadMoreTasks() {
    loadTasks(false);
}

function showCreateTaskModal() {
    const modal = new bootstrap.Modal(document.getElementById('createTaskModal'));
    modal.show();
}

async function handleCreateTask(e) {
    e.preventDefault();
    
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        project_id: parseInt(document.getElementById('taskProject').value),
        priority: document.getElementById('taskPriority').value,
        assigned_to_id: document.getElementById('taskAssignee').value ? 
            parseInt(document.getElementById('taskAssignee').value) : null
    };

    try {
        const response = await fetch('/api/v1/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
            modal.hide();
            document.getElementById('createTaskForm').reset();
            loadTasks(true);
            loadStats();
        } else {
            const error = await response.json();
            alert(`Error creating task: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error creating task:', error);
        alert('Error creating task. Please try again.');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await fetch(`/api/v1/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTasks(true);
            loadStats();
        } else {
            alert('Error deleting task');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        alert('Error deleting task. Please try again.');
    }
}

function editTask(taskId) {
    // For now, just show an alert - could implement edit modal
    alert(`Edit task ${taskId} - Feature to be implemented`);
}