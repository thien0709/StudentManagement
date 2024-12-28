window.addEventListener('DOMContentLoaded', async () => {
    const routes = ['/', '/class', '/input-score'];
    for (const route of routes) {
        try {
            // Gửi yêu cầu đến từng route bảo vệ
            const response = await fetch(route);

            if (!response.ok) {
                const result = await response.json();
                if (result.status === 'error') {
                    // Hiển thị thông báo lỗi nếu có
                    Swal.fire('Lỗi!', result.message, 'error');
                    return; // Nếu có lỗi, không tiếp tục kiểm tra các route khác
                }
            }
        } catch (error) {
            Swal.fire('Lỗi!', 'Đã xảy ra lỗi khi gửi yêu cầu.', 'error');
        }
    }
});
