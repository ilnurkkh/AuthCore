document.addEventListener('DOMContentLoaded', () => {

    const messageEl = document.getElementById('message');

    // Helper function to display messages
    const showMessage = (message, isError = false) => {
        if (!messageEl) return;
        messageEl.textContent = message;
        messageEl.className = 'message'; // Reset classes
        if (isError) {
            messageEl.classList.add('error');
        } else {
            messageEl.classList.add('success');
        }
    };

    // 1. Handle Registration
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());

            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            if (response.ok) {
                showMessage(result.message);
                registerForm.reset();
            } else {
                showMessage(result.error, true);
            }
        });
    }

    // 2. Handle Login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            // === START OF FIX: Removed syntax error ===
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            // === END OF FIX ===

            const result = await response.json();
            if (response.ok) {
                showMessage(result.message);
                loginForm.reset();
                // In a real app, you'd save a token and redirect
            } else {
                showMessage(result.error, true);
            }
        });
    }
    
    // 3. Handle Password Reset
    const resetForm = document.getElementById('reset-form');
    if (resetForm) {
        resetForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(resetForm);
            const data = Object.fromEntries(formData.entries());

            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            if (response.ok) {
                showMessage(result.message);
                resetForm.reset();
            } else {
                showMessage(result.error, true);
            }
        });
    }

    // 4. Handle User List Page
    const usersTableBody = document.getElementById('users-tbody');
    if (usersTableBody) {
        const fetchUsers = async () => {
            try {
                const response = await fetch('/api/users');
                if (!response.ok) {
                    const result = await response.json();
                    throw new Error(result.error || 'Failed to fetch users.');
                }
                const users = await response.json();
                
                usersTableBody.innerHTML = ''; // Clear existing
                users.forEach(user => {
                    const row = document.createElement('tr');
                    // Add hover effect classes
                    row.className = 'hover:bg-gray-700 transition duration-150';
                    
                    // Style the cells
                    row.innerHTML = `
                        <td class="py-4 px-6 text-sm text-gray-100">${user.id}</td>
                        <td class="py-4 px-6 text-sm text-gray-100">${user.username}</td>
                        <td class="py-4 px-6 text-sm text-gray-100">${user.failed_attempts}</td>
                        <td class="py-4 px-6 text-sm ${user.locked_out ? 'text-red-400 font-medium' : 'text-gray-100'}">
                            ${user.locked_out ? 'Yes' : 'No'}
                        </td>
                    `;
                    usersTableBody.appendChild(row);
                });

            } catch (err) {
                showMessage(err.message, true);
            }
        };
        fetchUsers();
    }

    // === START OF FIX: MOBILE MENU TOGGLE ===
    // 5. Handle Mobile Menu Toggle
    const menuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden'); // Toggles the 'hidden' class
        });
    }
    // === END OF FIX ===
});

