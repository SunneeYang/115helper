document.addEventListener('DOMContentLoaded', () => {
    // 获取按钮和输入框的引用
    const sendCookiesButton = document.getElementById('sendCookies');
    const serverAddressInput = document.getElementById('serverAddress');

    // Cookies发送成功后，显示自定义通知
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');

    const content = document.getElementById('content');
    const notLoggedInMessage = document.getElementById('notLoggedInMessage');

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.cookies.getAll({url: tabs[0].url}, (cookies) => {
            const list = document.getElementById('cookiesList');

            let neededCookies = cookies.filter(cookie => ['UID', 'CID', 'SEID'].includes(cookie.name));
            if (neededCookies.length > 0) {
                content.style.display = 'block';
                notLoggedInMessage.style.display = 'none';

                let cookiesString = cookies.map(cookie => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${cookie.name}: ${cookie.value}`;
                    list.appendChild(listItem);

                    return `${encodeURIComponent(cookie.name)}=${encodeURIComponent(cookie.value)}`
                }).join(';') + ';';

                // 现在 cookiesString 包含了所有键值对，用分号和一个空格分隔
                console.log(cookiesString); // 或者您可以在这里做其他事情，比如显示到页面上
                // 将 cookiesString 保存起来以便稍后发送
                sendCookiesButton.dataset.cookies = cookiesString;
            } else {
                content.style.display = 'none';
                notLoggedInMessage.style.display = 'block';
            }
        });
    });

    sendCookiesButton.addEventListener('click', () => {
        const cookiesString = sendCookiesButton.dataset.cookies;
        if (!cookiesString) {
            showNotification('No cookies to send', 'error')
            return;
        }

        // 获取用户输入的服务器地址
        const serverAddress = serverAddressInput.value;

        // 检查服务器地址是否合法
        if (!isValidServerAddress(serverAddress)) {
            showNotification('Invalid server address', 'error')
            return;
        }
        
        const endpoint = `${serverAddress}/115-cookies`;
        
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `cookies=${encodeURIComponent(cookiesString)}`
        })
        .then(response => {
            if (response.ok) {
                return response;
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            showNotification('Cookies sent successfully', 'success')
            console.log('Cookies sent successfully:', data);
        })
        .catch(error => {
            console.error('Error sending cookies:', error);
        });
    });
});

// 编写函数来验证服务器地址的合法性
function isValidServerAddress(address) {
    // 在此处添加服务器地址的验证逻辑，确保它是有效的
    // 示例：检查地址是否以 "http://" 或 "https://" 开头
    return address.startsWith('http://') || address.startsWith('https://');
}

let notificationTimeout = null; // 用于跟踪当前消息的 setTimeout

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');

    // 如果有消息正在显示，先关闭之前的消息
    closeNotification();

    // 设置消息和样式
    notificationText.textContent = message;
    notification.style.display = 'block';

    // 根据样式类型设置背景颜色
    if (type === 'success') {
        notification.style.backgroundColor = '#5cb85c';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#d9534f';
    }

    // 设置消息显示时间，1秒后自动关闭
    notificationTimeout = setTimeout(() => {
        closeNotification();
    }, 1000);
}

function closeNotification() {
    const notification = document.getElementById('notification');
    // 取消之前的 setTimeout
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
    notification.style.display = 'none';
}
