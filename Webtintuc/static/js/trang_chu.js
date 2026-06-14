// ==================== UTILITY FUNCTIONS ====================

// Cập nhật đồng hồ
function updateClock() {
    const clockElement = document.getElementById('clock');
    if (!clockElement) return;
    
    const today = new Date();
    
    const weekday = today.toLocaleDateString('vi-VN', {
        weekday: 'long'
    });
    
    const dateStr = `${weekday}, ${today.getDate()}/${today.getMonth() + 1}/${today.getFullYear()}`;
    clockElement.textContent = dateStr;
}

// Hiển thị modal đăng nhập
function showLogin() {
    const loginModal = document.getElementById('loginModal');
    if (loginModal) {
        loginModal.style.display = 'block';
    }
}

// Hiển thị modal đăng ký
function showRegister() {
    const registerModal = document.getElementById('registerModal');
    if (registerModal) {
        registerModal.style.display = 'block';
    }
}

// Đóng modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Chuyển giữa modal đăng nhập và đăng ký
function switchModal() {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (loginModal && registerModal) {
        if (loginModal.style.display === 'block') {
            loginModal.style.display = 'none';
            registerModal.style.display = 'block';
        } else {
            registerModal.style.display = 'none';
            loginModal.style.display = 'block';
        }
    }
}

// Sao chép link
function copyLink() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        alert('Đã sao chép link!');
    }).catch(() => {
        alert('Không thể sao chép link');
    });
}

// Đóng modal khi nhấp bên ngoài
window.onclick = function(event) {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (loginModal && event.target === loginModal) {
        loginModal.style.display = 'none';
    }
    if (registerModal && event.target === registerModal) {
        registerModal.style.display = 'none';
    }
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    // Cập nhật đồng hồ khi tải trang
    updateClock();
    
    // Cập nhật đồng hồ mỗi phút
    setInterval(updateClock, 60000);
    
    // Xử lý sự kiện form đăng nhập/đăng ký
    document.querySelectorAll('#loginModal form, #registerModal form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Chức năng này đang được phát triển. Vui lòng quay lại sau!');
        });
    });
});

// ==================== HELPER FUNCTIONS ====================

/**
 * Format ngày tháng năm
 * @param {Date} date - Ngày cần format
 * @param {String} format - Format cần (VN, EN, etc.)
 * @returns {String} - Ngày đã format
 */
function formatDate(date, format = 'VN') {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    if (format === 'VN') {
        return `${day}/${month}/${year}`;
    } else if (format === 'EN') {
        return `${year}-${month}-${day}`;
    }
    return dateStr;
}

/**
 * Hiển thị thông báo
 * @param {String} message - Thông báo
 * @param {String} type - Loại (success, error, warning, info)
 * @param {Number} duration - Thời gian hiển thị (ms)
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${
            type === 'success' ? '#d4edda' :
            type === 'error' ? '#f8d7da' :
            type === 'warning' ? '#fff3cd' :
            '#d1ecf1'
        };
        color: ${
            type === 'success' ? '#155724' :
            type === 'error' ? '#721c24' :
            type === 'warning' ? '#856404' :
            '#0c5460'
        };
        border: 1px solid ${
            type === 'success' ? '#c3e6cb' :
            type === 'error' ? '#f5c6cb' :
            type === 'warning' ? '#ffeeba' :
            '#bee5eb'
        };
        border-radius: 4px;
        z-index: 9999;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, duration);
}

/**
 * Kiểm tra email hợp lệ
 * @param {String} email - Email cần kiểm tra
 * @returns {Boolean} - True nếu email hợp lệ
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Truncate text
 * @param {String} text - Text cần truncate
 * @param {Number} length - Số ký tự tối đa
 * @returns {String} - Text đã truncate
 */
function truncateText(text, length = 100) {
    if (text.length <= length) {
        return text;
    }
    return text.substring(0, length) + '...';
}

// ==================== SMOOTH SCROLL ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
