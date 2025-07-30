function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function isAuthenticated() {
    const token = getToken();
    if (!token) return false;
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp > Date.now() / 1000;
    } catch {
        return false;
    }
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function setCurrentUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function logout() {
    removeToken();
    window.location.href = 'login.html';
}

async function login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
        const response = await fetch('/api/auth/token', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            
            const userResponse = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${data.access_token}`
                }
            });
            
            if (userResponse.ok) {
                const user = await userResponse.json();
                setCurrentUser(user);
                return { success: true };
            }
        } else {
            const error = await response.json();
            return { success: false, error: error.detail };
        }
    } catch (error) {
        return { success: false, error: 'Bağlantı hatası' };
    }
}
    
async function register(username, email, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        if (response.ok) {
            return { success: true };
        } else {
            const error = await response.json();
            return { success: false, error: error.detail };
        }
    } catch (error) {
        return { success: false, error: 'Bağlantı hatası' };
    }
}